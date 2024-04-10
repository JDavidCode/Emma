import json
import uuid
import traceback
from datetime import datetime
from app.config.config import Config
import os


class UserAuthAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)

    def user_login(self, info):
        email = info.get('email')
        password = info.get('password')
        try:
            # Crear un cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Consulta para obtener información del usuario por correo electrónico
            query = "SELECT * FROM users WHERE login = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()

            # Verificar si se encontró el usuario y la contraseña coincide
            if user_data and user_data["pass"] == password:
                return True, user_data["uid"]
            else:
                return False, "Credenciales incorrectas. Inicio de sesión fallido."

        except Exception as e:
            traceback_str = traceback.format_exc()
            return False, f"Error al ejecutar la consulta: login {traceback_str}"

    def user_signup(self, info):
        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Check if the user with the provided email already exists
            query_check_user = "SELECT COUNT(*) as count FROM users WHERE login = %s"
            cursor.execute(query_check_user, (info.get('email', ''),))
            user_count = cursor.fetchone().get('count', 0)

            if user_count > 0:
                return False, "User with this email already exists."

            # Generate IDs
            uid = self.generate_uuid()
            did = self.generate_id('DID-')
            cid = self.generate_id('CID-')
            gid = self.generate_id('GID-')

            # Calculate the age
            birthday = info.get('date')
            age = self.calculate_age(birthday)

            # Create chat
            chat_info = {
                "gid": gid,
                "name": "Hello World!",
                "description": "I'm Playing with EMMA",
            }

            # Convertir el diccionario a formato JSON
            content = json.dumps([self.create_prompt_session(
                info.get('name', ""), age, birthday, '1')])

            # Consulta para insertar el nuevo chat
            query = "INSERT INTO chats (cid,uid,  info, content) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (cid, uid, json.dumps(chat_info), content))

            try:
                # Confirmar la transacción
                self.users_conn.commit()
            except Exception as e:
                return False, f"Error creating user {e}"

            # Agregar el nuevo grupo a la lista existente
            nuevo_grupo = {"name": "Default",
                           "id": gid, "content": [cid]}

            # Create the new user
            nuevo_usuario = {
                "name": info.get('name', ""),
                "email": info.get('email', ""),
                "age": age,
                "birthday": birthday,
                "level": "1"
            }

            # Query to insert the new user
            query_insert_user = "INSERT INTO users (uid, info, login, pass, devices, cloud) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query_insert_user, (uid, json.dumps(nuevo_usuario), info.get('email', ""), info.get(
                'pass', ""), json.dumps([{"id": did, "device_name": "Unknown Device"}]), json.dumps([nuevo_grupo])))

            # Confirm the transaction
            self.users_conn.commit()

            return True, "User Registered"

        except Exception as e:
            print("Error al ejecutar la consulta: group ", e)
            import traceback
            traceback.print_exc()
            return False, "Error executing query: signup"

    def get_user(self, user_id):
        user_info = {}
        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Retrieve user information (excluding pass)
            query_get_user = "SELECT login, info, cloud FROM users WHERE uid = %s"
            cursor.execute(query_get_user, (user_id,))
            user_db_info = cursor.fetchone()

            if not user_db_info:
                return False, "User not found"

            # Modify the query_chats to use the correct JSON path expression for MySQL
            query_chats = "SELECT info, cid FROM chats WHERE uid = %s"
            cursor.execute(query_chats, (user_id,))
            user_db_chats = cursor.fetchall()
            formatted_chats = [
                {
                    'name': json.loads(chat['info'])['name'],
                    'description': json.loads(chat['info'])['description'],
                    'id': chat['cid'],
                    'gid': json.loads(chat['info'])['gid']
                }
                for chat in user_db_chats
            ]
            # Parse JSON data for user information
            user_info['info'] = json.loads(user_db_info['info'])
            user_info['groups'] = json.loads(user_db_info['cloud'])
            user_info['chats'] = formatted_chats

            return True, user_info

        except Exception as e:
            print("Error executing query: get_user", e)
            import traceback
            traceback.print_exc()  # Print the full traceback
            return False, "Error executing query: get_user"

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

    def _handle_system_ready(self):
        self.users_conn = Config.app.system.admin.agents.db.connect(
            os.getenv("DB_HOST"),
            os.getenv("DB_USER"),
            os.getenv("DB_USER_PW"),
            os.getenv("DB_NAME"))
        return True

    def handle_error(self, error, message=None):
        error_message = f"Error in {self.name}: {error}"
        if message:
            error_message += f" - {message}"
        traceback_str = traceback.format_exc()
        self.queue_handler.add_to_queue("LOGGING", (self.name, traceback_str))

    def _handle_shutdown(self):
        try:
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)
        except Exception as e:
            self.handle_error(e)


if __name__ == "__main__":
    # Sample usage or test cases can be added here
    pass
