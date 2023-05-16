import importlib
import subprocess
from emma.config.globals import FORGE_GLOBALS
from emma.config.globals import tools_da, tools_cs


class Builder:
    def __init__(self, package_name):
        print(f"Forge Builder is installing {package_name}...")
        self._service = importlib.import_module(
            "emma.forge.handlers.package_handler.PackageHandler")()
        self.package_name = package_name
        self.has_custom = False
        self.unpackage(package_name)
        self.run(package_name)

    def unpackage(self):
        tools_cs.ToolKit.unzipper(
            (f"./emma/.EmmaRootUser/.temp/{self.package_name}.zip", "./emma/integration_services/"))

    def service_register(self, config_path):
        service_data = tools_da.yaml_loader(config_path)
        if service_data["custom_packages"] == True:
            self.has_custom = True
        self._service.add_service(service_data)

    def create_instance(self):
        FORGE_GLOBALS.create_instance()

    def install_dependencies(self):
        requirements_file = f"./emma/integration_services/{self.package_name}/requirements.txt"
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

    def run(self):
        self.package_source = f"./emma/integration_services/{self.package_name}"
        self.service_register(
            f"{self.package_source}/config/forge_config.yml")
        self.install_dependencies()
        if self.has_custom:
            self.install_custom_packages()
        self.create_instances()
