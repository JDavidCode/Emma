import threading
from collections import defaultdict


class NetworkHandler:
    def __init__(self, queue_handler, console_handler):
        self.console_handler = console_handler
        self.queue_handler = queue_handler
        self.event = threading.Event()
        self.stop_flag = False
        self.user_network = defaultdict(lambda: defaultdict(dict))
        self.lock = threading.Lock()

    def add_user_session(self, user_id, session_info):
        # Add a session to the user's sessions list
        with self.lock:
            if 'user_sessions' not in self.user_network[user_id]:
                self.user_network[user_id]['user_sessions'] = []
            self.user_network[user_id]['user_sessions'].append(session_info)

    def register_session(self, user_id, device_name, device_id, session_info, public_ip=None):
        with self.lock:
            if user_id not in self.user_network:
                self.user_network[user_id] = {
                    'devices': [{
                        'device_id': device_id,
                        'device_name': device_name,
                        'sessions': [session_info] if session_info else [],
                        'public_ips': [public_ip] if public_ip else []
                    }],
                    'user_sessions': []  # New user_sessions list for the user
                }
            else:
                if 'devices' not in self.user_network[user_id]:
                    self.user_network[user_id]['devices'] = []

                existing_device = next(
                    (device for device in self.user_network[user_id]['devices'] if device['device_id'] == device_id), None)

                if existing_device:
                    if session_info:
                        if 'sessions' in existing_device:
                            if session_info not in existing_device['sessions']:
                                existing_device['sessions'].append(
                                    session_info)
                        else:
                            existing_device['sessions'] = [session_info]

                    if public_ip:
                        if 'public_ips' in existing_device:
                            if public_ip not in existing_device['public_ips']:
                                existing_device['public_ips'].append(public_ip)
                        else:
                            existing_device['public_ips'] = [public_ip]
                else:
                    new_device = {
                        'device_id': device_id,
                        'device_name': device_name,
                        'sessions': [session_info] if session_info else [],
                        'public_ips': [public_ip] if public_ip else []
                    }
                    self.user_network[user_id]['devices'].append(new_device)

    def get_user_devices(self, user_id):
        with self.lock:
            user_data = self.user_network.get(user_id, {})
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
            for user_id, user_data in self.user_network.items():
                for device in user_data['devices']:
                    for session in device['sessions']:
                        if session['session_id'] == session_id:
                            return user_id, device['device_name'], session
        return None, None, None

    def verify_session(self, session_id):
        with self.lock:
            for user_id, user_data in self.user_network.items():
                for device in user_data['devices']:
                    for session in device['sessions']:
                        if session['session_id'] == session_id:
                            return True
        return False

    def get_knowed_user_sessions(self, user_id):
        with self.lock:
            user_data = self.user_network.get(user_id, {})
            sessions = []
            for device in user_data.get('devices', []):
                for session in device.get('sessions', []):
                    sessions.append(session)
            return sessions

    def get_known_sessions(self):
        with self.lock:
            all_sessions = []
            for user_id, user_data in self.user_network.items():
                for device in user_data['devices']:
                    for session in device['sessions']:
                        all_sessions.append(session)
            return all_sessions

    def get_user_network(self, user_id):
        with self.lock:
            return dict(self.user_network.get(user_id, {}))

    def clear_all_sessions_from_user(self, user_id):
        with self.lock:
            if user_id in self.user_network:
                del self.user_network[user_id]

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            session_data = self.queue_handler.get_queue('NET_SESSIONS')
            if session_data:
                user_id, device_info = list(session_data.items())[0]
                device_name = device_info['device_name']
                device_id = device_info['device_id']
                # Get the session name, or None if it doesn't exist
                session_name = device_info['session'].get('session_name')
                session_id = device_info['session'].get('session_id')
                # Get the public IP, or None if it doesn't exist
                public_ip = device_info.get('public_ip')

                # Make sure session_name exists before registering the session
                if session_name is not None:
                    session_info = {
                        'session_name': session_name,
                        'session_id': session_id
                    }

                    self.register_session(
                        user_id, device_name, device_id, session_info, public_ip)
                else:
                    # Handle the case when 'session_name' is missing
                    print("Missing session_name for session data:", device_info)

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    # Sample usage or test cases can be added here
    pass
