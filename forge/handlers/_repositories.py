import os
import logging

class RepositoryHandler:
    CONFIG_FILE_PATH = "./forge/config/config.yml"

    def __init__(self, tools=[]):
        self.tools_da, self.tools_cs = tools
        self.packages = {}
        self.load_data()

    def load_data(self):
        try:
            self.packages = self.tools_da.yaml_loader(
                self.CONFIG_FILE_PATH, "repositories")
        except Exception as e:
            logging.error(f"Error loading data: {e}")

    def save_data(self):
        data = {"repositories": self.packages, "version": "1.0"}
        try:
            self.tools_da.yaml_saver(self.CONFIG_FILE_PATH, data)
        except Exception as e:
            logging.error(f"Error saving data: {e}")

    def add_repository(self, package, repository):
        if package in self.packages:
            logging.warning("The repository already exists.")
        else:
            self.packages[package] = repository
            self.save_data()

    def get_repository(self, package):
        return self.packages.get(package, [])

    def verify_repository(self, package_name):
        if package_name in self.packages:
            package_directory = f"./app/services/external/{package_name}"
            if os.path.exists(package_directory):
                logging.info("Package is downloaded.")
                return True
            else:
                logging.warning(
                    "The repository exists, but the package was not found. It will be installed automatically.")
                return False
        return False

    def remove_repository(self, package):
        if package in self.packages:
            del self.packages[package]
            self.save_data()
            return True
        return False

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    pass  # Add your application logic here
