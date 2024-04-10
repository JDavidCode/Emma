from datetime import datetime
import json
import traceback
from app.config.config import Config
import os


class UserGroupsAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)

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

    def _handle_system_ready(self):
        self.users_conn = Config.app.system.admin.agents.db.connect(os.getenv(
            "DB_HOST"), os.getenv("DB_USER"), os.getenv("DB_USER_PW"), os.getenv("DB_NAME"))
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
