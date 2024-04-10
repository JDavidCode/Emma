import json
import traceback
from app.config.config import Config
from sqlalchemy import Integer, MetaData, Table, Column, String, JSON
import os

class UserChatsAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)

    def get_chat(self, chat_id, user_id):
        if user_id is None or chat_id is None:
            return "User ID and Chat ID cannot be null."

        try:
            # Define table metadata
            metadata = MetaData()
            chats_table = Table('chats', metadata,
                                Column('cid', Integer, primary_key=True),
                                Column('uid', Integer),
                                Column('info', JSON),
                                Column('content', JSON)
                                )

            # Create a database session
            with self.engine.begin() as session:
                # Query for the chat using SQLAlchemy syntax
                result = session.query(chats_table) \
                    .filter(chats_table.cid == chat_id) \
                    .filter(chats_table.uid == user_id) \
                    .first()

                if result:
                    # Check user access to the chat
                    chat_info = result.info
                    if chat_info.get('uid') == user_id:
                        # Return chat data as a dictionary
                        chat_data = {
                            'info': {
                                "name": chat_info.get('name', ""),
                                "description": chat_info.get('description', ""),
                            },
                            'content': result.content
                        }
                        return chat_data
                    else:
                        return "User does not have access to this chat."
                else:
                    return "Chat not found."

        except Exception as e:
            self.handle_error(e)
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
            prompt = self.create_prompt_session(name, age, birthday, level)

        chat_info = {
            "gid": group_id,
            "name": name,
            "description": description,
        }

        try:
            # Define table metadata
            metadata = MetaData()
            chats_table = Table('chats', metadata,
                                # Assuming cid is a string
                                Column('cid', String, primary_key=True),
                                Column('uid', Integer),
                                Column('info', JSON),
                                Column('content', JSON)
                                )
            users_table = Table('users', metadata,  # Assuming a users table exists
                                Column('uid', Integer, primary_key=True),
                                Column('cloud', JSON)
                                )

            # Create a database session
            with self.engine.begin() as session:
                # Insert chat data
                new_chat = chats_table(
                    cid=chat_id, uid=_id, info=chat_info, content=json.dumps([prompt]))
                session.add(new_chat)

                # Update user's cloud (assuming cloud is a JSON column)
                user = session.query(users_table).filter(users_table.uid == _id).filter(
                    users_table.cloud.op('->>')['id'] == group_id).first()

                if user:  # Check if user exists in the specified cloud
                    current_cloud = user.cloud or []  # Default to empty list if None
                    if chat_id not in current_cloud:
                        current_cloud.append(chat_id)
                        user.cloud = current_cloud
                else:
                    print(f"User with ID {_id} not found in group {group_id}.")

                # Commit changes
                session.commit()

                return True, (f"Chat {name} has been created", name)

        except Exception as e:
            self.handle_error(e)
            return False, "ERROR DATABASE OPERATION"
        
    def edit_chat(self, uid, chat_id, name=None, description=None):
        if chat_id is None:
            return "Chat ID cannot be null"

        try:
            # Define table metadata
            metadata = MetaData()
            chats_table = Table('chats', metadata,
                Column('cid', String, primary_key=True),  # Assuming cid is a string
                Column('uid', Integer),
                Column('info', JSON),
                Column('content', JSON)
            )

            # Create a database session
            with self.engine.begin() as session:
                # Query for the chat
                chat = session.query(chats_table) \
                    .filter(chats_table.cid == chat_id) \
                    .filter(chats_table.uid == uid) \
                    .first()

                if not chat:
                    return False, f"Chat with ID {chat_id} not found"

                # Update chat information if new values are provided
                if name is not None:
                    chat.info['name'] = name
                if description is not None:
                    chat.info['description'] = description

                # Commit changes (no need to convert to JSON as SQLAlchemy handles it)
                session.commit()

                return True, f"Chat with ID {chat_id} has been updated"

        except Exception as e:
            self.handle_error(e)
            return False, "Error executing query: update_chat"

    def update_chat(self, uid, chat_id, content):
        if chat_id is None:
            return "Chat ID cannot be null"

        try:
            # Define table metadata
            metadata = MetaData()
            chats_table = Table('chats', metadata,
                                # Assuming cid is a string
                                Column('cid', String, primary_key=True),
                                Column('uid', Integer),
                                Column('info', JSON),
                                Column('content', JSON)
                                )

            # Create a database session
            with self.engine.begin() as session:
                # Query for the chat
                chat = session.query(chats_table) \
                    .filter(chats_table.cid == chat_id) \
                    .filter(chats_table.uid == uid) \
                    .first()

                if not chat:
                    return False, f"Chat with ID {chat_id} not found"

                # Update content (clear and concise)
                chat.content = content

                # Commit changes
                session.commit()

                return True, f"Chat with ID {chat_id} has been updated"

        except Exception as e:
            self.handle_error(e)
            return False, "Error executing query: update_chat"


    def remove_chat(self, uid, gid, cid):
        if cid is None:
            return "Chat ID cannot be null"

        try:
            # Define table metadata
            metadata = MetaData()
            chats_table = Table('chats', metadata,
                                # Assuming cid is a string
                                Column('cid', String, primary_key=True),
                                Column('uid', Integer),
                                Column('info', JSON),
                                Column('content', JSON)
                                )
            users_table = Table('users', metadata,  # Assuming a users table exists
                                Column('uid', Integer, primary_key=True),
                                Column('cloud', JSON)
                                )

            # Create a database session
            with self.engine.begin() as session:
                # Delete chat from database (efficient)
                session.query(chats_table).filter(chats_table.cid == cid).delete()

                # Update user's cloud (if applicable, assuming cloud is a list)
                user = session.query(users_table).filter(users_table.uid == uid).filter(
                    users_table.cloud.op('->>')['id'] == gid).first()

                if user and user.cloud:  # Only update if user and cloud exist
                    try:
                        current_cloud = json.loads(user.cloud)
                        if cid in current_cloud:
                            current_cloud.remove(cid)
                            user.cloud = json.dumps(
                                current_cloud)  # Update cloud JSON
                    except Exception as e:  # Handle potential JSON parsing errors
                        print(
                            f"Error parsing user cloud for ID {uid} (group {gid}):", e)

                # Commit changes
                session.commit()

                return True, f"Chat with ID {cid} has been removed"

        except Exception as e:
            self.handle_error(e)
            return False

    def _handle_system_ready(self):
        self.engine = Config.app.system.admin.agents.db.connect(os.getenv("DB_HOST"), os.getenv("DB_USER"), os.getenv("DB_USER_PW"), os.getenv("DB_NAME"))
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
