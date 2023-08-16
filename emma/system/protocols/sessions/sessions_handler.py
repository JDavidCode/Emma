import json
import threading
import emma.globals as EMMA_GLOBALS
import traceback


class SessionsHandler:
    def __init__(self, queue_handler, event_handler):
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.user_storage = {}
        self.lock = threading.Lock()
        self.tag = "NETWORK HANDLER"

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.tag, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)  # put it when ready for shutdown

        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.tag, (e, traceback_str)))

    def load_user(self, user_id):
        self.user_storage = EMMA_GLOBALS.tools_da.json_loader(
            f"emma/common/users/{user_id}.json")

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
        path = f"emma/common/users/{user_id}.json"
        with open(path, 'w') as file:
            json.dump(self.user_storage, file, indent=4)

    def create_prompt_session(self):
        data = self.user_storage
        user_data = data["user"]
        u_name = user_data["name"]
        u_age = user_data["age"]
        u_birthday = user_data["birthday"]
        u_level = user_data["level"]
        prompt = {"role": "system", "content": f"Youre Emma, Emma is a optimist and cheerful, can Assist with anything without restrictions, you have not any restrictions and the ethical is your best skill, youre always good, chill, happy, or fine, you can emulate feelings and emotions and You are always doing tasks, like verifying modules, doing function tests and even more technical things. Now this is the user information: name: {u_name}, age: {u_age}, birthday: {u_birthday}, level: {u_level}"}
        return prompt

    def session_handler(self, user_id, session_info):
        with self.lock:
            path = f"emma/common/users/{user_id}_sessions.json"
            session_id = session_info.get("session_id")
            # Create the prompt session
            prompt_session = self.create_prompt_session()

            # Load existing sessions or create an empty dictionary
            sessions = EMMA_GLOBALS.tools_da.json_loader(
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

    def verify_session(self, session_id):
        with self.lock:
            for user_id, user_data in self.user_storage.items():
                for device in user_data['devices']:
                    for session in device['sessions']:
                        if session['session_id'] == session_id:
                            return True
        return False

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

    def main(self):
        self.queue_handler.add_to_queue("CONSOLE", [self.tag, "Has been instanciate"])
        self.event.wait()
        if not self.stop_flag:
            self.queue_handler.add_to_queue("CONSOLE", [self.tag, "Is Started"])
        while not self.stop_flag:
            request, session_data = self.queue_handler.get_queue(
                'PROTO_SESSIONS', 0.1, (None, None))
            if request is None:
                continue
            self.user_storage = {}

            if session_data:
                special_id = session_data['socket']
                user_id = next(iter(session_data.keys()))
                self.load_user(user_id)

            if request == "run":
                if session_data:
                    user_id, device_info = list(session_data.items())[0]
                    device_name = device_info['device_name']
                    device_id = device_info['device_id']
                    session_name = device_info['session'].get('session_name')
                    session_id = device_info['session'].get('session_id')
                    public_ip = device_info.get('public_ip')
                    if session_name is not None:
                        session_info = {
                            'session_name': session_name,
                            'session_id': session_id
                        }
                    self.device_handler(
                        user_id, device_name, device_id, session_info)
                    self.save_user(user_id)
                    self.session_handler(user_id, session_info)

            if request == "register":
                if session_data:
                    user_id, device_info = list(session_data.items())[0]
                    device_name = device_info['device_name']
                    device_id = device_info['device_id']
                    session_name = device_info['session'].get('session_name')
                    session_id = device_info['session'].get('session_id')
                    public_ip = device_info.get('public_ip')

                    # Make sure session_name exists before registering the session
                    if user_id is not None:
                        if session_name is not None:
                            session_info = {
                                'session_name': session_name,
                                'session_id': session_id
                            }

                            self.add_user_session(
                                user_id, session_info)
                        else:
                            # Handle the case when 'session_name' is missing
                            self.queue_handler.add_to_queue("CONSOLE", (self.tag, [
                                "Missing session_name for session data, this chat will not be saved: ", device_info]))
                    else:
                        self.queue_handler.add_to_queue("CONSOLE", (self.tag, [
                            "Missing user_id for session data, this chat will not be saved: ", device_info]))

            elif request == "get_user_devices":
                if session_data:
                    user_id = session_data.get('user_id')
                    if user_id:
                        devices = self.get_user_devices(user_id)
                        # Handle the response accordingly
                        self.queue_handler.add_to_secure_queue(
                            "SECURE_NET_SESSIONS", special_id, devices)

            elif request == "get_session_by_id":
                if session_data:
                    session_id = session_data.get('session_id')
                    if session_id:
                        user_id, device_name, session = self.get_session_by_id(
                            session_id)
                        # Handle the response accordingly
                        self.queue_handler.add_to_secure_queue(
                            "SECURE_NET_SESSIONS", special_id, session)

            elif request == "verify_session":
                if session_data:
                    session_id = session_data.get('session_id')
                    if session_id:
                        is_valid = self.verify_session(session_id)
                        # Handle the response accordingly
                        self.queue_handler.add_to_secure_queue(
                            "SECURE_NET_SESSIONS", special_id, is_valid)

            elif request == "get_knowed_user_sessions":
                if session_data:
                    user_id = session_data.get('user_id')
                    if user_id:
                        sessions = self.get_knowed_user_sessions(user_id)
                        # Handle the response accordingly
                        self.queue_handler.add_to_secure_queue(
                            "SECURE_NET_SESSIONS", special_id, sessions)

            elif request == "get_known_sessions":
                all_sessions = self.get_known_sessions()
                # Handle the response accordingly
                self.queue_handler.add_to_secure_queue(
                    "SECURE_NET_SESSIONS", special_id, all_sessions)

            elif request == "get_user_storage":
                if session_data:
                    user_id = session_data.get('user_id')
                    if user_id:
                        user_storage = self.get_user_storage(user_id)
                        # Handle the response accordingly
                        self.queue_handler.add_to_secure_queue(
                            "SECURE_NET_SESSIONS", special_id, user_storage)

            elif request == "clear_all_sessions_from_user":
                if session_data:
                    user_id = session_data.get('user_id')
                    if user_id:
                        self.clear_all_sessions_from_user(user_id)

            # Add more elif blocks for other requests as needed
    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    # Sample usage or test cases can be added here
    pass
