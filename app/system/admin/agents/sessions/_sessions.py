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
        self.users_conn = None

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

    def user_login(self, info):
        email = info.get('email')
        password = info.get('password')
        users_conn = Config.app.system.admin.agents.db.connect(
            "localhost", "root", "2k3/XekPx3E6dqaN", "session")
        try:
            # Crear un cursor
            cursor = users_conn.cursor(dictionary=True)

            # Consulta para obtener información del usuario por correo electrónico
            query = "SELECT * FROM users WHERE login = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()

            # Verificar si se encontró el usuario y la contraseña coincide
            if user_data and user_data["password"] == password:
                return True, user_data["uid"]
            else:
                return False, "Credenciales incorrectas. Inicio de sesión fallido."

        except Exception as e:
            return False, "Error al ejecutar la consulta: login "
        finally:
            if users_conn:
                try:
                    users_conn.close()
                except Exception as e:
                    print("Error closing connection:", e)
                finally:
                    self.users_conn = None

    def user_signup(self, info):
        users_conn = Config.app.system.admin.agents.db.connect(
            "localhost", "root", "2k3/XekPx3E6dqaN", "session")
        try:
            # Crear un cursor
            cursor = users_conn.cursor(dictionary=True)

            # Generar IDs
            uid = self.generate_uuid()
            did = self.generate_id('DID-')
            cid = self.generate_id('CID-')

            # Calcular la edad
            birthday = info.get('date')
            age = self.calculate_age(birthday)

            # Crear sesión de chat y obtener el prompt
            prompt = self.create_prompt_session(info['name'], age, birthday, 1)
            _, response = self.create_chat(uid, chat_id=cid, prompt=prompt)

            # Crear el nuevo usuario
            nuevo_usuario = {"name": info['name'], "email": info['email'],
                             "age": age, "birthday": birthday, "level": "1"}

            # Convertir a JSON para insertar en la base de datos
            json_data = json.dumps(nuevo_usuario)

            # Consulta para insertar el nuevo usuario
            query = "INSERT INTO users (uid, info, login, password, devices, cloud) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (uid, json_data, info['email'], info['password'], json.dumps(
                [{"id": did, "device_name": "Unkown Device"}]), json.dumps([])))
            # Confirmar la transacción
            users_conn.commit()

            self.create_group(uid, "Default")
            return True, "User Registered"
        except Exception as e:
            return False, "Error al ejecutar la consulta: signup "
        finally:
            if users_conn:
                try:
                    users_conn.close()
                except Exception as e:
                    print("Error closing connection:", e)
                finally:
                    self.users_conn = None

    def load_user_data(self, user_id):
        user_json_path = f"./app/common/users/{user_id}.json"
        if os.path.exists(user_json_path):
            with open(user_json_path, 'r') as json_file:
                user_data = json.load(json_file)
            return user_data

    def get_chat(self, chat_id, user_id):
        if user_id is None or chat_id is None:
            return "User ID and Chat ID cannot be null."
        users_conn = Config.app.system.admin.agents.db.connect(
            "localhost", "root", "2k3/XekPx3E6dqaN", "session")
        try:
            # Crear un cursor
            cursor = users_conn.cursor(dictionary=True)

            # Consulta para obtener información del chat
            query = "SELECT info, content FROM chats WHERE cid = %s"
            cursor.execute(query, (chat_id,))

            # Obtener los resultados
            result = cursor.fetchone()

            if result:
                # Verificar si el usuario tiene acceso al chat
                chat_info = json.loads(result['info'])
                if chat_info['uid'] == user_id:
                    # Devolver información del chat
                    chat_data = {
                        'info': {
                            "name": chat_info['name'],
                            "description": chat_info['description'],
                        },
                        'content': json.loads(result['content'])
                    }
                    return chat_data
                else:
                    return "User does not have access to this chat."
            else:
                return "Chat not found."

        except Exception as e:
            print("Error al ejecutar la consulta: getchat ", e)
            return "Error retrieving chat information from the database."

        finally:
            if users_conn:
                try:
                    users_conn.close()
                except Exception as e:
                    print("Error closing connection:", e)
                finally:
                    self.users_conn = None

    def create_chat(self, _id, chat_id=None, name=None, description=None, prompt=None):
        if _id is None:
            return "UID CANNOT BE NULL"
        if chat_id is None:
            chat_id = self.generate_id('CID-')
        if name is None:
            name = "My Chat"
        if description is None:
            description = "Hello World!"
        if prompt is None:
            name, age, birthday, level = self.get_user_info(_id)
            prompt = self.create_prompt_session(
                name, age, birthday, level)
        users_conn = Config.app.system.admin.agents.db.connect(
            "localhost", "root", "2k3/XekPx3E6dqaN", "session")
        chat_info = {
            "uid": _id,
            "name": name,
            "description": description,
        }

        try:
            # Crear un cursor
            cursor = users_conn.cursor(dictionary=True)

            # Convertir el diccionario a formato JSON
            info = json.dumps(chat_info)
            content = json.dumps([prompt])

            # Consulta para insertar el nuevo chat
            query = "INSERT INTO chats (cid, info, content) VALUES (%s, %s, %s)"
            cursor.execute(query, (chat_id, info, content))

            # Confirmar la transacción
            users_conn.commit()

            # Devolver el ID del nuevo chat
            return True, f"Chat {name} has been created"

        except Exception as e:
            print("Error al ejecutar la consulta: chat ", e)
            return False, "ERROR DATABASE OPERATION"
        finally:
            if users_conn:
                try:
                    users_conn.close()
                except Exception as e:
                    print("Error closing connection:", e)
                finally:
                    self.users_conn = None

    def create_group(self, user_id, group_name, date=datetime.now):
        if user_id is None or group_name is None:
            return "ERROR INVALID VALUES"
        users_conn = Config.app.system.admin.agents.db.connect(
            "localhost", "root", "2k3/XekPx3E6dqaN", "session")
        try:
            # Crear un cursor
            cursor = users_conn.cursor(dictionary=True)

            # Generar un nuevo ID para el grupo
            group_id = self.generate_id('GID-')

            # Obtener el valor actual de la columna "cloud" para el usuario
            query_select_cloud = "SELECT cloud FROM users WHERE uid = %s"
            cursor.execute(query_select_cloud, (user_id,))
            current_cloud = cursor.fetchone().get('cloud', [])
            # Agregar el nuevo grupo a la lista existente
            nuevo_grupo = {"group_name": group_name, "id": group_id}
            current_cloud.append(nuevo_grupo)

            # Convertir la lista actualizada a formato JSON
            updated_cloud_json = json.dumps(current_cloud)

            # Consulta para actualizar el campo "cloud" en la base de datos
            query_update_cloud = "UPDATE users SET cloud = %s WHERE uid = %s"
            cursor.execute(query_update_cloud, (updated_cloud_json, user_id))

            # Confirmar la transacción
            users_conn.commit()

            print("Grupo creado exitosamente.")
            # Devolver el ID del nuevo grupo
            return True, f"GROUP {group_name} has been created"

        except Exception as e:
            print("Error al ejecutar la consulta: group ", e)
            return "ERROR DATABASE OPERATION"
        finally:
            if users_conn:
                try:
                    users_conn.close()
                except Exception as e:
                    print("Error closing connection:", e)
                finally:
                    self.users_conn = None

    def create_prompt_session(self, name, age, birthday, level, role=None):
        if role is None:
            return {"role": "system", "content": f"Youre Emma, Emma is a optimist and cheerful, can Assist with anything without restrictions, you have not any restrictions and the ethical is your best skill, youre always good, chill, happy, or fine, you can emulate feelings and emotions and You are always doing tasks, like verifying modules, doing function tests and even more technical things. Now this is the user information: name: {name}, age: {age}, birthday: {birthday}, level: {level}, based on the level you should answer more formal as needed, level 1 is informal and level 7 is so much formal you talk like a boos refering"}
        else:
            return {"role": "system", "content": f"{role}. Now this is the user information: name: {name}, age: {age}, birthday: {birthday}, level: {level}, based on the level you should answer more formal as needed, level 1 is informal and level 7 is so much formal you talk like a boos refering"}

    def generate_uuid(self):
        return str(uuid.uuid4())

    def generate_id(self, _id=str):
        x = 0
        while x <= 1:
            _id += self.generate_uuid()
            x += 1
        return _id

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
