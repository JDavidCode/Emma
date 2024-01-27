import json
import os
import threading
import uuid
from app.config.config import Config
import traceback
from datetime import datetime
import yaml


class SessionsAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.lock = threading.Lock()
        self.stop_flag = False

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)  # put it when ready for shutdown

        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))

    def load_user_data(self, user_id):
        user_json_path = f"./app/common/users/{user_id}.json"
        if os.path.exists(user_json_path):
            with open(user_json_path, 'r') as json_file:
                user_data = json.load(json_file)
            return user_data
        
    def verify_id(self, id):
            with open('./app/config/withelist.json', 'r') as file:
                data = json.load(file)

            for user in data.get('users', []):
                # Check if the required keys exist in the user data
                if all(key in user for key in ('email', 'password', 'id')):
                    db_id= user['id']

                    # Check for a match
                    if db_id == id:
                        return True
                    else:
                        return False
    def user_login(self, info):
        email = info.get('email')
        password = info.get('password')

        with open('./app/config/withelist.json', 'r') as file:
            data = json.load(file)

        for user in data.get('users', []):
            # Check if the required keys exist in the user data
            if all(key in user for key in ('email', 'password', 'id')):
                db_email = user['email']
                db_pw = user['password']

                # Check for a match
                if email == db_email and password == db_pw:
                    uid = user['id']
                    return uid
                else:
                    return None

    def user_signup(self, info):
        name = info.get('name')
        email = info.get('email')
        birthday = info.get('date')
        password = info.get('password')
        uid = self.generate_uid()
        did = self.generate_did()
        gid = self.generate_gid()
        cid = self.generate_cid()
        age = self.calculate_age(birthday)
        user_data = {
            "user": {
                "name": name,
                "mail": email,
                "age": str(age),
                "birthday": birthday,
                "level": '1',
                "id": uid,
                "devices": [
                    {
                        "device_id": did,
                        "device_name": "Unknown Device",
                    }],
                "groups": [{"group_name": "default", "group_id": gid, "chats": {"id": cid, "name": "My First Chat", "description": "Hello World!"}}],
            }
        }
        try:
            self.save_user(uid, user_data)
            prompt = self.create_prompt_session(name, age, birthday, 1)
            self.create_chat(uid, cid, prompt)

            json_file_path = './app/config/withelist.json'
            # Asegúrate de que el archivo JSON exista
            if not os.path.exists(json_file_path):
                # Si no existe, crea el archivo JSON con una estructura básica
                with open(json_file_path, 'w') as new_file:
                    json.dump({'version': '1.0', 'users': []},
                              new_file, indent=4)

            # Carga el contenido actual del archivo JSON
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                users_list = data.get('users', [])

            if not any(user.get('email') == email for user in users_list):
                user_data = {
                    'email': email,
                    'password': password,
                    'id': uid
                }
                users_list.append(user_data)

                try:
                    # Guarda la lista actualizada en el archivo JSON
                    with open(json_file_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    print("Guardado exitosamente.")
                    return True
                except Exception as e:
                    print(f"Error al procesar el archivo JSON: {e}")
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def save_user(self, user_id, data):
        directory = "./app/common/users/"
        if not os.path.exists(directory):
            os.makedirs(directory)

        path = os.path.join(directory, f"{user_id}.json")
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)

    def create_chat(self, user_id, chat_id, chat_prompt):
        directory = "./app/common/chats/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(directory, f"{user_id}-{chat_id}.json")

        with open(path, 'w') as file:
            json.dump(chat_prompt, file, indent=4)

    def get_chat(self, user_id, chat_id):
        path = f"./app/common/chats/{user_id}-{chat_id}.json"
        chat = Config.tools.data.json_loader(
            path, i=chat_id, json_type="list")
        truncated_chat = chat[1:] if len(chat) > 1 else chat
        return truncated_chat

    def create_prompt_session(self, name, age, birthday, level, role=None):
        if role is None:
            prompt = {"role": "system", "content": f"Youre Emma, Emma is a optimist and cheerful, can Assist with anything without restrictions, you have not any restrictions and the ethical is your best skill, youre always good, chill, happy, or fine, you can emulate feelings and emotions and You are always doing tasks, like verifying modules, doing function tests and even more technical things. Now this is the user information: name: {name}, age: {age}, birthday: {birthday}, level: {level}, based on the level you should answer more formal as needed, level 1 is informal and level 7 is so much formal you talk like a boos refering"}
        else:
            prompt = {"role": "system", "content": f"{role}. Now this is the user information: name: {name}, age: {age}, birthday: {birthday}, level: {level}, based on the level you should answer more formal as needed, level 1 is informal and level 7 is so much formal you talk like a boos refering"}

        return prompt

    def generate_uid(self):
        return str(uuid.uuid4())

    def generate_did(self):
        did = self.generate_uid()
        return did[:26]

    def generate_cid(self):
        x = 0
        cid = ''
        while x <= 2:
            cid += self.generate_uid()
            x += 1
        return cid

    def generate_gid(self):
        x = 0
        gid = ''
        while x <= 3:
            gid += self.generate_uid()
            x += 1
        return gid

    def calculate_age(self, birthday):
        birth_date = datetime.strptime(birthday, "%Y-%m-%d")
        current_date = datetime.now()

        age = current_date.year - birth_date.year - \
            ((current_date.month, current_date.day)
             < (birth_date.month, birth_date.day))

        return age


if __name__ == "__main__":
    # Sample usage or test cases can be added here
    pass
