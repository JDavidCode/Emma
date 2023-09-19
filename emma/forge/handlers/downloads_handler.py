import hashlib
import requests


class DownloadsHandler:
    def __init__(self, tools=[]):
        self.tools_da, self.tools_cs = tools

    def download_package(self, repository, package_name):
        save_path = f"emma/forge/.temp/forge_{package_name}.zip"
        try:
            response = requests.get(repository)
            response.raise_for_status()  # Check for any errors
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"{package_name} has been downloaded!")
            return True  # self.verify_integrity(package_name)
        except Exception as e:
            print(
                f"some error ocurred while trying to download {package_name}: \n {e}")
            return False

    def verify_integrity(self, package_name):
        print(f"{package_name} verifyin integrity... \n please wait...")
        expected_checksum = 1234  # DB verify if not in db continue with precaution
        path = f"emma/forge/.temp/forge_{package_name}.zip"
        downloaded_checksum = self.calculate_checksum(path)
        if downloaded_checksum == expected_checksum:
            print("Integrity check passed. The file is not corrupted.")
            return True
        else:
            print("Integrity check failed. The file may be corrupted.")
            return False

    def calculate_checksum(file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
