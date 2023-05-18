import os


class RepositoryHandler:
    def __init__(self, tools=[]):
        self.tools_cs, self.tools_da = tools
        self.file_path = "./emma/forge/config/config.yml"
        self.packages = {}
        self.load_data()

    def load_data(self):
        self.packages = self.tools_da.yaml_loader(
            self.file_path, "repositories")

    def save_data(self):
        data = {"repositories": self.packages, "version": "1.0", }
        self.tools_da.yaml_saver(self.file_path, data)

    def add_repository(self, package, repository):
        if package in self.packages:
            print("the repository already exist.")
        else:
            self.packages[package] = repository
        self.save_data()

    def get_package_repositories(self, package):
        if package in self.packages:
            return self.packages[package]
        return []

    def verify_repository(self, package_name):
        if package_name in self.packages:
            if os.path.exists(f"./emma/services/external/{package_name}"):
                print("Package is downloaded")
                return True
            else:
                print(
                    "The repository exist, but the package was not found, this will be installed automatically.")
                return False
        return False

    def remove_package(self, package):
        if package in self.packages:
            del self.packages[package]
            self.save_data()
            return True
        return False
