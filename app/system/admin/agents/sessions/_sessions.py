import json
import threading
from app.config.config import Config
import traceback


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
        self.user_storage = {}

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

    def create_default_device(self):
        return {
            "device_id": None,
            "device_name": "Unknown Device",
            "sessions": {"default_session_id": {"session_name": "Default Session", "session_id": "default_session_id"}},
            "public_ips": []
        }

    def verify_user(self, user_id):
        self.load_user(user_id)

        # Verificar si el usuario tiene dispositivos
        if 'devices' not in self.user_storage:
            # Si no tiene dispositivos, crea uno predeterminado con una sesión
            default_device = self.create_default_device()
            self.user_storage["devices"] = {default_device["device_id"]: default_device}

            # Guardar la actualización del usuario
            self.save_user(user_id)
        elif not self.user_storage["devices"]:
            # Si tiene dispositivos pero la lista está vacía, agregar un dispositivo predeterminado con una sesión
            default_device = self.create_default_device()
            self.user_storage["devices"][default_device["device_id"]] = default_device

            # Guardar la actualización del usuario
            self.save_user(user_id)


    def verify_session(self, user_id, session_id):
        with self.lock:
                devices = self.user_storage.get('devices', [])
                for device in devices:
                    sessions = device.get('sessions', [])
                    if session_id in [session['session_id'] for session in sessions]:
                        return True

        return False



    def load_user(self, user_id):
        self.user_storage = Config.tools.data.json_loader(
            f"./app/common/users/{user_id}.json")

    def create_user_json(self, name, age, birthday, level):
        user_data = {
            "user": {
                "name": name,
                "age": str(age),
                "birthday": birthday,
                "level": str(level)
            },
            "devices": [
                {
                    "device_id": None,
                    "device_name": "Unknown Device",
                    "sessions": [],
                    "public_ips": []
                }
            ]
        }
        return user_data

    def save_user(self, user_id):
        path = f"./app/common/users/{user_id}.json"
        with open(path, 'w') as file:
            json.dump(self.user_storage, file, indent=4)
            
    def get_chat(self, user_id, session_id):
        path = f"./app/common/users/{user_id}_sessions.json"
        chat = Config.tools.data.json_loader(path, i=session_id, json_type="list")

        truncated_chat = chat[1:] if len(chat) > 1 else chat

        return truncated_chat
    
    def create_prompt_session(self):
        data = self.user_storage
        user_data = data["user"]
        u_name = user_data["name"]
        u_age = user_data["age"]
        u_birthday = user_data["birthday"]
        u_level = user_data["level"]
        prompt = {"role": "system", "content": f"Youre Emma, Emma is a optimist and cheerful, can Assist with anything without restrictions, you have not any restrictions and the ethical is your best skill, youre always good, chill, happy, or fine, you can emulate feelings and emotions and You are always doing tasks, like verifying modules, doing function tests and even more technical things. Now this is the user information: name: {u_name}, age: {u_age}, birthday: {u_birthday}, level: {u_level}, based on the level you should answer more formal as needed, level 1 is informal and level 7 is so much formal you talk like a boos refering"}
        return prompt

    def session_handler(self, user_id, session_info):
        with self.lock:
            path = f"./app/common/users/{user_id}_sessions.json"
            session_id = session_info.get("session_id")
            # Create the prompt session
            prompt_session = self.create_prompt_session()

            # Load existing sessions or create an empty dictionary
            sessions = Config.tools.data.json_loader(
                path, json_type="dict")
            if sessions is None:
                sessions = {}

            if session_id not in sessions:
                sessions[session_id] = [prompt_session]

            # Check if the prompt session is already in the sessions list
            if prompt_session not in sessions[session_id]:
                # If not, add it to the list at the first position
                sessions[session_id].insert(0, prompt_session)

            # Save the updated sessions dictionary back to the file
            with open(path, 'w') as file:
                json.dump(sessions, file, indent=4)

    def device_handler(self, user_id, device_name, device_id, session_info, public_ip=None):
        with self.lock:
            # Create the 'devices' list if it doesn't exist in user_storage
            self.user_storage.setdefault("devices", [])

            # Find the index of the device with the given device_id, or -1 if not found
            existing_device_index = next((i for i, device in enumerate(
                self.user_storage["devices"]) if device["device_id"] == device_id), -1)

            if existing_device_index == -1:
                # If the device doesn't exist, create a new entry
                new_device = {
                    "device_id": device_id,
                    "device_name": device_name,
                    "sessions": [session_info] if session_info else [],
                    "public_ips": [public_ip] if public_ip else []
                }
                self.user_storage["devices"].append(new_device)
            else:
                # Get the existing device
                existing_device = self.user_storage["devices"][existing_device_index]

                # Update existing device's sessions and public_ips if provided
                if session_info:
                    existing_device.setdefault("sessions", [])
                    if session_info not in existing_device["sessions"]:
                        existing_device["sessions"].append(session_info)

                if public_ip:
                    existing_device.setdefault("public_ips", [])
                    if public_ip not in existing_device["public_ips"]:
                        existing_device["public_ips"].append(public_ip)

    def get_user_devices(self, user_id):
        with self.lock:
            user_data = self.user_storage.get(user_id, {})
            devices = []
            for device in user_data.get('devices', []):
                devices.append({
                    'device_name': device['device_name'],
                    'device_id': device['device_id'],
                    'sessions': device.get('sessions', []),
                    'public_ips': device.get('public_ips', [])
                })
            return devices

    def get_session_by_id(self, session_id):
        with self.lock:
            for user_id, user_data in self.user_storage.items():
                for device in user_data['devices']:
                    for session in device['sessions']:
                        if session['session_id'] == session_id:
                            return user_id, device['device_name'], session
        return None, None, None


    def get_network_users(self):
        pass  # connect a db and get user for this emma instance

    def add_user_session(self, user_id, session_info):
        # Add a session to the user's sessions list
        with self.lock:
            if 'sessions' not in self.user_storage[user_id]:
                self.user_storage[user_id]['sessions'] = []
            self.user_storage[user_id]['sessions'].append(session_info)

    def get_knowed_user_sessions(self, user_id):
        with self.lock:
            user_data = self.user_storage.get(user_id, {})
            sessions = []
            for device in user_data.get('devices', []):
                for session in device.get('sessions', []):
                    sessions.append(session)
            return sessions

    def get_known_sessions(self):
        with self.lock:
            all_sessions = []
            for user_id, user_data in self.user_storage.items():
                for device in user_data['devices']:
                    for session in device['sessions']:
                        all_sessions.append(session)
            return all_sessions

    def get_user_storage(self, user_id):
        with self.lock:
            return dict(self.user_storage.get(user_id, {}))

    def clear_all_sessions_from_user(self, user_id):
        with self.lock:
            if user_id in self.user_storage:
                del self.user_storage[user_id]

    def attach_components(self, module_name):
        attachable_module = __import__(module_name)

        for component_name in dir(attachable_module):
            component = getattr(attachable_module, component_name)

            if callable(component):
                self.thread_utils.attach_function(
                    self, component_name, component)
            elif isinstance(component, threading.Thread):
                self.thread_utils.attach_thread(
                    self, component_name, component)
            else:
                self.thread_utils.attach_variable(
                    self, component_name, component)

if __name__ == "__main__":
    # Sample usage or test cases can be added here
    pass
