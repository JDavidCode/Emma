import importlib
import subprocess
from emma.config.globals import FORGE_GLOBALS


class Builder:
    def __init__(self, package_name, tools=[]):
        self.tools_cs, self.tools_da = tools
        print(f"Forge Builder is installing {package_name}...")
        _service = importlib.import_module(
            "emma.forge.handlers.service_handler")
        self._service = _service.ServiceHandler(tools)
        self.package_name = package_name
        self.endpoint = ""
        self.args = []
        self.has_custom = False

    def unpackage(self):
        self.tools_cs.unzipper(
            [(f"./emma/.EmmaRootUser/.temp/forge_{self.package_name}.zip", "./emma/services/external/")])

    def service_register(self, config_path):
        service_data = self.tools_da.yaml_loader(config_path, "forge_service")
        service_data = service_data[0]
        self.has_custom = service_data.get('custom_packages', False)
        self.endpoint = service_data.get('endpoint')
        self._service.add_service(service_data)

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

    def run(self):
        self.unpackage()
        self.package_source = f"./emma/services/external/{self.package_name}"
        self.service_register(
            f"{self.package_source}/config/config.yml")
        self.install_dependencies()
        if self.has_custom:
            self.install_custom_packages()
        FORGE_GLOBALS().create_instance(self.package_name, self.endpoint)
