from cryptography.fernet import Fernet


class KeyManager:
    def __init__(self, key_file):
        self.key_file = key_file

    def generate_key(self) -> bytes:
        key = Fernet.generate_key()
        self._write_key(key)
        return key

    def load_key(self) -> bytes:
        with open(self.key_file, "rb") as file:
            key = file.read()
        return key

    def _write_key(self, key: bytes) -> None:
        with open(self.key_file, "wb") as file:
            file.write(key)

    def save_key(self):
        pass
