from datetime import datetime
import json


class UserChatsAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)

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
