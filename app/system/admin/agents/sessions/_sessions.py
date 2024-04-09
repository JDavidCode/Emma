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

    def _handle_system_ready(self):
        #self.users_conn = Config.app.system.admin.agents.db.connect(
        #    os.getenv("db_host"), os.getenv(
        #        "db_user"), os.getenv("db_pw"), os.getenv("db_name"))
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

    def get_chat(self, chat_id, user_id):
        if user_id is None or chat_id is None:
            return "User ID and Chat ID cannot be null."
        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Query to obtain information of the chat
            query = "SELECT info, content FROM chats WHERE cid = %s & uid = %s"
            cursor.execute(query, (chat_id, user_id))

            # Get the results
            result = cursor.fetchone()

            if result:
                # Verify if the user has access to the chat
                chat_info = json.loads(result['info'])
                if chat_info.get('uid') == user_id:
                    # Return information of the chat
                    chat_data = {
                        'info': {
                            "name": chat_info.get('name', ""),
                            "description": chat_info.get('description', ""),
                        },
                        'content': json.loads(result['content'])
                    }
                    return chat_data
                else:
                    return "User does not have access to this chat."
            else:
                return "Chat not found."

        except Exception as e:
            print("Error executing query: get_chat ", e)
            return "Error retrieving chat information from the database."

    def create_chat(self, _id, group_id, name=None, description=None, prompt=None):
        if _id is None:
            return "UID CANNOT BE NULL"
        chat_id = self.generate_id('CID-')
        if name is None:
            name = "My Chat"
        if description is None:
            description = "Hello World!"
        if prompt is None:
            name, age, birthday, level = self.get_user_info(_id)
            prompt = self.create_prompt_session(
                name, age, birthday, level)

        chat_info = {
            "gid": group_id,
            "name": name,
            "description": description,
        }

        try:
            # Crear un cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Convertir el diccionario a formato JSON
            info = json.dumps(chat_info)
            content = json.dumps([prompt])

            # Consulta para insertar el nuevo chat
            query = "INSERT INTO chats (cid, uid, info, content) VALUES (%s,%s, %s, %s)"
            cursor.execute(query, (chat_id, _id, info, content))

            # Confirmar la transacción
            self.users_conn.commit()

            # Select the current 'cloud' from the database
            query_select_cloud = "SELECT cloud FROM users WHERE uid = %s AND cloud->>'id'=%s"
            cursor.execute(query_select_cloud, (_id, group_id))
            # Default to an empty list if 'cloud' is None
            current_cloud_json = cursor.fetchone().get('cloud', '[]')

            # Convert the JSON string to a Python list
            current_cloud_list = json.loads(current_cloud_json)

            # Assuming 'chat_id' is the variable holding the chat ID you want to add
            chat_id = 'example_chat_id'

            # Check if the 'chat_id' is not already in the list before adding
            if chat_id not in current_cloud_list:
                # Add the 'chat_id' to the list
                current_cloud_list.append(chat_id)

                # Convert the modified list back to a JSON string
                updated_cloud_json = json.dumps(current_cloud_list)

                # Update the 'cloud' in the database with the modified JSON string
                query_update_cloud = "UPDATE users SET cloud = %s WHERE uid = %s & cloud->>'id'=%s"
                cursor.execute(query_update_cloud,
                               (updated_cloud_json, _id, group_id))

                # Confirm the transaction after the update
                self.users_conn.commit()
            else:
                print(f"Chat ID {chat_id} already exists in the list.")
            return True, (f"Chat {name} has been created", name)

        except Exception as e:
            print("Error al ejecutar la consulta: chat ", e)
            return False, "ERROR DATABASE OPERATION"

    def edit_chat(self, uid, chat_id, name=None, description=None):
        if chat_id is None:
            return "Chat ID cannot be null"

        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Retrieve existing chat information
            query_get_chat = "SELECT info, content FROM chats WHERE cid = %s & uid = %s"
            cursor.execute(query_get_chat, (chat_id, uid))
            chat_info = cursor.fetchone()

            if not chat_info:
                return False, f"Chat with ID {chat_id} not found"

            # Parse JSON data for chat information
            chat_info['info'] = json.loads(chat_info['info'])
            chat_info['content'] = json.loads(chat_info['content'])

            # Update chat information if new values are provided
            if name is not None:
                chat_info['info']['name'] = name
            if description is not None:
                chat_info['info']['description'] = description

            # Convert the updated information back to JSON
            updated_info = json.dumps(chat_info['info'])
            updated_content = json.dumps(chat_info['content'])

            # Update the chat in the database
            query_update_chat = "UPDATE chats SET info = %s, content = %s WHERE cid = %s"
            cursor.execute(query_update_chat,
                           (updated_info, updated_content, chat_id))

            # Confirm the transaction
            self.users_conn.commit()

            return True, f"Chat with ID {chat_id} has been updated"

        except Exception as e:
            print("Error executing query: update_chat", e)
            return False, "Error executing query: update_chat"

    def update_chat(self, uid, chat_id, content):
        if chat_id is None:
            return "Chat ID cannot be null"

        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Update the chat in the database
            query_update_chat = "UPDATE chats SET content = %s WHERE cid = %s & uid = %s"
            cursor.execute(query_update_chat,
                           ("updated_content", chat_id, uid))

            # Confirm the transaction
            self.users_conn.commit()

            return True, f"Chat with ID {chat_id} has been updated"

        except Exception as e:
            print("Error executing query: update_chat", e)
            return False, "Error executing query: update_chat"

    def remove_chat(self, uid, gid, cid):
        if cid is None:
            return "Chat ID cannot be null"

        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Update the content field in the user's cloud
            query_update_cloud = "UPDATE users SET cloud = JSON_SET(cloud, '$[%s].content', %s) WHERE JSON_CONTAINS_PATH(cloud, 'one', '$[%s]')"
            cursor.execute(query_update_cloud, (cid,
                           json.dumps(), gid))

            # Delete the chat from the database
            query_remove_chat = "DELETE FROM chats WHERE cid = %s"
            cursor.execute(query_remove_chat, (cid,))

            # Confirm the transaction
            self.users_conn.commit()

            return True, f"Chat with ID {cid} has been removed"

        except Exception as e:
            print("Error executing query: remove_chat", e)
            return False, "Error executing query: remove_chat"

    def create_group(self, user_id, name, content=[], date=datetime.now):
        if user_id is None or name is None:
            return "ERROR INVALID VALUES"

        try:
            # Crear un cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Generar un nuevo ID para el grupo
            group_id = self.generate_id('GID-')

            # Obtener el valor actual de la columna "cloud" para el usuario
            query_select_cloud = "SELECT cloud FROM users WHERE uid = %s"
            cursor.execute(query_select_cloud, (user_id,))
            # Default to an empty list if 'cloud' is None
            current_cloud_json = cursor.fetchone().get('cloud', '[]')
            current_cloud = json.loads(current_cloud_json)

            # If 'content' is provided, use it; otherwise, initialize as an empty list
            content = content or []

            # Agregar el nuevo grupo a la lista existente
            nuevo_grupo = {"name": name,
                           "id": group_id, "content": content}
            current_cloud.append(nuevo_grupo)

            # Convertir la lista actualizada a formato JSON
            updated_cloud_json = json.dumps(current_cloud)

            # Consulta para actualizar el campo "cloud" en la base de datos
            query_update_cloud = "UPDATE users SET cloud = %s WHERE uid = %s"
            cursor.execute(query_update_cloud, (updated_cloud_json, user_id))

            # Confirmar la transacción
            self.users_conn.commit()

            print("Grupo creado exitosamente.")
            # Devolver el ID del nuevo grupo
            return True, (f"GROUP {name} has been created", name)

        except Exception as e:
            print("Error al ejecutar la consulta: group ", e)
            import traceback
            traceback.print_exc()  # Print the full traceback
            return False, "ERROR DATABASE OPERATION"

    def edit_group(self, user_id, from_group_id, to_group_id, content_add, content_remove):
        if user_id is None or from_group_id is None or to_group_id is None:
            return "ERROR INVALID VALUES"

        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Obtaining the current value of the "cloud" column for the user
            query_select_cloud = "SELECT cloud FROM users WHERE uid = %s"
            cursor.execute(query_select_cloud, (user_id,))
            current_cloud = cursor.fetchone().get('cloud', [])

            # Find the index of the group to update and check if it exists
            from_group_index = None
            for index, group in enumerate(current_cloud):
                if group.get('id') == from_group_id:
                    from_group_index = index
                    break

            if from_group_index is None:
                return "ERROR GROUP NOT FOUND"

            # Remove content from the specified group
            if content_remove:
                current_content = current_cloud[from_group_index].get(
                    'content', [])
                updated_content = [
                    item for item in current_content if item not in content_remove]
                current_cloud[from_group_index]['content'] = updated_content

            # Add content to the new group
            to_group_exists = False
            for group in current_cloud:
                if group.get('id') == to_group_id:
                    to_group_exists = True
                    group['content'].extend(content_add)
                    break

            if not to_group_exists:
                return "ERROR TO GROUP NOT FOUND"

            # Convert the updated list to JSON
            updated_cloud_json = json.dumps(current_cloud)

            # Update the "cloud" column in the database
            query_update_cloud = "UPDATE users SET cloud = %s WHERE uid = %s"
            cursor.execute(query_update_cloud, (updated_cloud_json, user_id))

            # Confirm the transaction
            self.users_conn.commit()

            print("Grupo actualizado exitosamente.")
            return True, f"GROUP {from_group_id} has been updated"

        except Exception as e:
            print("Error executing query: group update", e)
            return "ERROR DATABASE OPERATION"

    def delete_group(self, user_id, group_id):
        if user_id is None or group_id is None:
            return "ERROR INVALID VALUES"

        try:
            # Create a cursor
            cursor = self.users_conn.cursor(dictionary=True)

            # Get the current value of the "cloud" column for the user
            query_select_cloud = "SELECT cloud FROM users WHERE uid = %s"
            cursor.execute(query_select_cloud, (user_id,))
            current_cloud = cursor.fetchone().get('cloud', [])

            # Check if the group exists in the user's cloud
            group_exists = any(
                group['id'] == group_id for group in current_cloud)

            if not group_exists:
                return False, f"Group with ID {group_id} not found"

            # Remove the group from the user's cloud
            updated_cloud = [
                group for group in current_cloud if group['id'] != group_id]

            # Convert the updated list to JSON
            updated_cloud_json = json.dumps(updated_cloud)

            # Update the "cloud" field in the database
            query_update_cloud = "UPDATE users SET cloud = %s WHERE uid = %s"
            cursor.execute(query_update_cloud, (updated_cloud_json, user_id))

            # Remove chats associated with the group
            query_remove_chats = "DELETE FROM chats WHERE info->>'gid' = %s"
            cursor.execute(query_remove_chats, (group_id,))

            # Confirm the transaction
            self.users_conn.commit()

            print(
                f"Group with ID {group_id} and associated chats have been removed successfully.")
            return True, f"Group with ID {group_id} has been removed"

        except Exception as e:
            print("Error executing query: remove_group", e)
            return False, "ERROR DATABASE OPERATION"

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
