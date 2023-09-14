import threading


class SessionManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.sessions = {}

    def add_session(self, session_id, user_id, device_id, session_info, public_ip=None):
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'user_id': user_id,
                    'device_id': device_id,
                    'session_info': session_info,
                    'public_ip': public_ip
                }

    def remove_session(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]

    def get_session_info(self, session_id):
        return self.sessions.get(session_id, None)
