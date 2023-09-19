import threading


class DeviceManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.user_network = {}

    def block_device(self, user_id, device_id):
        with self.lock:
            if user_id in self.user_network and 'devices' in self.user_network[user_id]:
                for device in self.user_network[user_id]['devices']:
                    if device['device_id'] == device_id:
                        device['blocked'] = True
                        break

    def set_device_password(self, user_id, device_id, password):
        with self.lock:
            if user_id in self.user_network and 'devices' in self.user_network[user_id]:
                for device in self.user_network[user_id]['devices']:
                    if device['device_id'] == device_id:
                        device['password'] = password
                        break
