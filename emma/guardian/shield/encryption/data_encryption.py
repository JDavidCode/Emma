from cryptography.fernet import Fernet


class Encryptor:
    def file_encrypt(self, key: bytes, original_file: str, encrypted_file: str) -> None:
        f = Fernet(key)

        with open(original_file, "rb") as file:
            original = file.read()

        encrypted = f.encrypt(original)

        with open(encrypted_file, "wb") as file:
            file.write(encrypted)

    def file_decrypt(
        self, key: bytes, encrypted_file: str, decrypted_file: str
    ) -> None:
        f = Fernet(key)

        with open(encrypted_file, "rb") as file:
            encrypted = file.read()

        decrypted = f.decrypt(encrypted)

        with open(decrypted_file, "wb") as file:
            file.write(decrypted)
