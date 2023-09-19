import hashlib
import requests
import logging

class DownloadsHandler:
    def __init__(self, tools=[]):
        self.tools_da, self.tools_cs = tools

    def download_package(self, repository, package_name):
        save_path = f"./forge/.temp/forge_{package_name}.zip"
        try:
            response = requests.get(repository)
            response.raise_for_status()  # Check for any errors
            with open(save_path, "wb") as file:
                file.write(response.content)
            logging.info(f"{package_name} has been downloaded!")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {package_name}: {e}")
            return False

    def verify_integrity(self, package_name):
        logging.info(f"Verifying integrity of {package_name}...")

        expected_checksum = "your_expected_checksum_here"  # Replace with the actual expected checksum
        path = f"./forge/.temp/forge_{package_name}.zip"
        downloaded_checksum = self.calculate_checksum(path)

        if downloaded_checksum == expected_checksum:
            logging.info("Integrity check passed. The file is not corrupted.")
            return True
        else:
            logging.error("Integrity check failed. The file may be corrupted.")
            return False

    @staticmethod
    def calculate_checksum(file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    pass  # Add your application logic here
