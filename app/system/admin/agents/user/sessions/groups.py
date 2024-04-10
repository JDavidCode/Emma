from datetime import datetime
import json
import traceback
from app.config.config import Config
import os
from sqlalchemy import Integer, MetaData, Table, Column, String, JSON, DateTime

class UserGroupsAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)


    def create_group(self, user_id, name, content=[], date=datetime.now()):
        if user_id is None or name is None:
            return "ERROR INVALID VALUES"

        try:
            # Define table metadata
            metadata = MetaData()
            users_table = Table('users', metadata,
                                Column('uid', Integer, primary_key=True),
                                Column('cloud', JSON)
                                )

            # Create a database session
            with self.engine.begin() as session:
                # Query for the user
                user = session.query(users_table).filter(
                    users_table.uid == user_id).first()

                if not user:
                    return False, f"User with ID {user_id} not found"

                # Generate a new group ID (assuming you have a separate function)
                group_id = self.generate_id('GID-')

                # Prepare group data (assuming content is a list)
                new_group = {"name": name, "id": group_id,
                             "content": content or []}

                # Update user's cloud (assuming cloud is a JSON column)
                current_cloud = user.cloud or []  # Default to empty list if None
                current_cloud.append(new_group)
                user.cloud = current_cloud

                # Commit changes
                session.commit()

                print("Grupo creado exitosamente.")
                return True, (f"GROUP {name} has been created", name)

        except Exception as e:
            self.handle_error(e)
            return False, "ERROR DATABASE OPERATION"

    def edit_group(self, user_id, from_group_id, to_group_id, content_add=[], content_remove=[]):
        if user_id is None or from_group_id is None or to_group_id is None:
            return "ERROR INVALID VALUES"

        try:
            # Define table metadata
            metadata = MetaData()
            users_table = Table('users', metadata,
                Column('uid', Integer, primary_key=True),
                Column('cloud', JSON)
            )

            # Create a database session
            with self.engine.begin() as session:
                # Query for the user
                user = session.query(users_table).filter(users_table.uid == user_id).first()

                if not user:
                    return False, f"User with ID {user_id} not found"

                # Find the group to update
                from_group = session.query(users_table.c.cloud) \
                    .filter(users_table.uid == user_id) \
                    .filter(users_table.c.cloud.op('->>')['id'] == from_group_id).first()

                if not from_group:
                    return False, "ERROR GROUP NOT FOUND"

                # Update content within the from_group (if provided)
                from_group_data = json.loads(from_group[0])
                current_content = from_group_data.get('content', [])
                if content_remove:
                    updated_content = [item for item in current_content if item not in content_remove]
                    from_group_data['content'] = updated_content

                # Find or create the to_group (assuming cloud is a list)
                to_group_data = None
                for group in user.cloud or []:  # Check if cloud exists and is a list
                    if group['id'] == to_group_id:
                        to_group_data = group
                        break

                if not to_group_data:
                    # Create a new group if not found
                    to_group_data = {"name": "New Group", "id": to_group_id, "content": []}
                    user.cloud.append(to_group_data)

                # Add content to the to_group # Update the user's cloud
                to_group_data['content'].extend(content_add)
                user.cloud = from_group_data and user.cloud or [from_group_data]  # Handle potential None values

                # Commit changes
                session.commit()

                print("Grupo actualizado exitosamente.")
                return True, f"GROUP {from_group_id} has been updated"

        except Exception as e:
            self.handle_error(e)
            return False, "ERROR DATABASE OPERATION"

    def delete_group(self, user_id, group_id):
        if user_id is None or group_id is None:
            return "ERROR INVALID VALUES"

        try:
            # Define table metadata
            metadata = MetaData()
            users_table = Table('users', metadata,
                Column('uid', Integer, primary_key=True),
                Column('cloud', JSON)
            )
            chats_table = Table('chats', metadata,
                Column('cid', String, primary_key=True),  # Assuming cid is a string
                Column('info', JSON)
            )

            # Create a database session
            with self.engine.begin() as session:
                # Query for the user
                user = session.query(users_table).filter(users_table.uid == user_id).first()

                if not user:
                    return False, f"User with ID {user_id} not found"

                # Check if the group exists (using list comprehension)
                group_to_delete = [group for group in user.cloud or [] if group['id'] == group_id]

                if not group_to_delete:
                    return False, f"Group with ID {group_id} not found"

                # Remove the group from user's cloud
                user.cloud = [group for group in user.cloud or [] if group['id'] != group_id]

                # Delete chats associated with the group
                session.query(chats_table).filter(chats_table.c.info.op('->>')['gid'] == group_id).delete()

                # Commit changes
                session.commit()

                print(
                    f"Group with ID {group_id} and associated chats have been removed successfully.")
                return True, f"Group with ID {group_id} has been removed"

        except Exception as e:
            self.handle_error(e)
            return False, "ERROR DATABASE OPERATION"

    def _handle_system_ready(self):
        self.engine = Config.app.system.admin.agents.db.connect(os.getenv(
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
