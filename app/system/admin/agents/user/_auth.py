import json
import uuid
import traceback
from datetime import datetime
from app.config.config import Config
import os
from sqlalchemy import Integer, MetaData, Table, Column, String, Boolean,JSON

class UserAuthAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)


    def user_login(self, engine, info):
        email = info.get('email')
        password = info.get('password')

        try:
            # Define table metadata
            metadata = MetaData()
            users_table = Table('users', metadata,
                                Column('uid', Integer, primary_key=True),
                                Column('login', String),
                                Column('_pass', String),
                                Column('active', Boolean)
                                )

            # Create a database session
            with engine.begin() as session:
                # Query for the user
                user = session.query(users_table).filter(
                    users_table.c.login == email).first()

                # Check if user exists and password matches
                if user and user._pass == password and user.active:
                    return True, user.uid
                else:
                    return False, "Incorrect credentials. Login failed."

        except Exception as e:
            self.handle_error(e)
            return False, "Error executing query: login"

    def user_signup(self, engine, info):
        try:
            # Define table metadata
            metadata = MetaData()
            users_table = Table('users', metadata,
                Column('uid', Integer, primary_key=True),
                Column('info', JSON),
                Column('login', String),
                Column('_pass', String),
                Column('devices', JSON),
                Column('cloud', JSON)
            )
            chats_table = Table('chats', metadata,
                Column('cid', String, primary_key=True),
                Column('uid', Integer),
                Column('info', JSON),
                Column('content', JSON)
            )

            # Create a database session
            with engine.begin() as session:
                # Check if user exists (using SQLAlchemy query)
                existing_user = session.query(users_table).filter(users_table.c.login == info.get('email', '')).first()

                if existing_user:
                    return False, "User with this email already exists."

                # Generate IDs (assuming you have separate functions)
                uid = self.generate_uuid()
                did = self.generate_id('DID-')
                cid = self.generate_id('CID-')
                gid = self.generate_id('GID-')

                # Calculate the age
                birthday = info.get('date')
                age = self.calculate_age(birthday)

                # Create chat data
                chat_info = {
                    "gid": gid,
                    "name": "Hello World!",
                    "description": "I'm Playing with EMMA",
                }

                # Create initial prompt session content (assuming a function)
                content = json.dumps([self.create_prompt_session(
                    info.get('name', ""), age, birthday, '1')])

                # Create new chat object
                new_chat = chats_table.insert().values(cid=cid, uid=uid, info=chat_info, content=content)
                session.execute(new_chat)

                # Create new user data
                new_user = {
                    "name": info.get('name', ""),
                    "email": info.get('email', ""),
                    "age": age,
                    "birthday": birthday,
                    "level": "1"
                }
                user_devices = [{
                    "id": did,
                    "device_name": "Unknown Device"
                }]
                user_cloud = [{"name": "Default", "id": gid, "content": [cid]}]

                # Create new user object
                new_user_obj = users_table.insert().values(
                    uid=uid, info=new_user, login=info.get('email', ""), _pass=info.get('pass', ""), devices=user_devices, cloud=user_cloud)
                session.execute(new_user_obj)

                # Commit changes
                session.commit()

                return True, "User Registered"

        except Exception as e:
            self.handle_error(e)
            return False, "Error executing query: signup"

    def get_user(self, engine, user_id):
        try:
            # Define table metadata
            metadata = MetaData()
            users_table = Table('users', metadata,
                Column('uid', Integer, primary_key=True),
                Column('login', String),
                Column('info', JSON),
                Column('cloud', JSON)
            )
            chats_table = Table('chats', metadata,
                Column('cid', String, primary_key=True),
                Column('uid', Integer),
                Column('info', JSON)
            )

            # Create a database session
            with engine.begin() as session:
                # Query for the user with relevant information
                user = session.query(users_table.c.login, users_table.c.info, users_table.c.cloud) \
                    .filter(users_table.c.uid == user_id).first()

                if not user:
                    return False, "User not found"

                # Construct user data dictionary
                user_info = {
                    "login": user.login,
                    "info": user.info,
                    "groups": user.cloud,
                    "chats": []  # Empty list for chats
                }

                # Query for chats (avoiding JSON parsing within the query)
                chats = session.query(chats_table.c.info, chats_table.c.cid).filter(chats_table.c.uid == user_id).all()

                # Format chat data
                user_info["chats"] = [
                    {
                        "name": chat[0]["name"],
                        "description": chat[0]["description"],
                        "id": chat[1],
                        "gid": chat[0]["gid"],
                    }
                    for chat in chats
                ]

                return True, user_info
        except Exception as e:
            self.handle_error(e)
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
