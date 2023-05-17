import importlib
import subprocess
from emma.config.globals import FORGE_GLOBALS


class Builder:
    def __init__(self, tools=[]):
        self.tools_cs, self.tools_da = tools
        _service = importlib.import_module(
            "emma.forge.handlers.service_handler")
        self._service = _service.ServiceHandler(tools)

        _repository = importlib.import_module(
            "emma.forge.handlers.repository_handler")
        self._repository = _repository.RepositoryHandler(tools)
        _download = importlib.import_module(
            "emma.forge.handlers.downloads_handler")
        self._download = _download.DownloadsHandler(tools)
        self.tools_cs, self.tools_da = tools

        self.package_name = ""
        self.endpoint = ""
        self.args = []
        self.has_custom = False
        self.service_data = {}

    def unpackage(self):
        self.tools_cs.unzipper(
            [(f"./emma/.EmmaRootUser/.temp/forge_{self.package_name}.zip", "./emma/services/external/")])

    def load_service_data(self):
        service_data = self._service.get_service(self.package_name)
        self.service_data = service_data
        self.has_custom = service_data.get('custom_packages', False)
        self.endpoint = service_data.get('endpoint')

    def service_register(self):
        service_data = self.tools_da.yaml_loader(
            f"./emma/services/external/{self.package_name}/config/config.yml", "forge_service")
        service_data = service_data[0]
        self.has_custom = service_data.get('custom_packages', False)
        self.endpoint = service_data.get('endpoint')
        self._service.add_service(service_data)

    def service_updater(self):
        pass

    def build(self):
        self.load_service_data()
        self.install_dependencies()
        if self.has_custom:
            self.install_custom_packages()
        FORGE_GLOBALS().create_instance(self.package_name, self.endpoint)

    def install_dependencies(self):
        requirements_file = f"./emma/services/external/{self.package_name}/requirements.txt"
        try:
            with open(requirements_file, "r") as file:
                for line in file:
                    package = line.strip()
                    subprocess.check_call(["pip", "install", package])
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")

    def install_custom_packages(self):
        pass

    def run(self, package_list):
        for package in package_list:
            self.package_name = package.get('package_name')
            repository = package.get('repository')
            print(f"Forge Builder is installing {self.package_name}...")
            if not all([repository, self.package_name]):
                print(f"{self.package_name} has Missing required parameters")
                continue

            print(f"Known {self.package_name} package repositories:",
                  self._repository.get_package_repositories(self.package_name))
            if not self._repository.verify_repository(self.package_name):
                self._repository.add_repository(self.package_name, repository)
                key = self._download.download_package(
                    repository, self.package_name)
                if key:
                    print(f"Installing {self.package_name}")
                    self.unpackage()
                    self.service_register()
                    self.build()
            else:
                if self._service.verify_service(self.package_name):
                    print(f"Building {self.package_name}")
                    self.build()
                else:
                    print(f"Installing local {self.package_name}")
                    self.service_register()
                    self.build()
                continue
