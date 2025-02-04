import importlib
import logging
import os
import subprocess
import tarfile
import threading
import glob
from app.config.config import Config


class Builder:
    def __init__(self,  name, queue_name, tools=[]):
        self.name = name
        self.queue_name = queue_name
        self.tools_da, self.tools_cs = tools
        _service = importlib.import_module(
            "forge.handlers._services")
        self._service = _service.ServiceHandler(tools)

        _repository = importlib.import_module(
            "forge.handlers._repositories")
        self._repository = _repository.RepositoryHandler(tools)
        _download = importlib.import_module(
            "forge.handlers._downloads")
        self._download = _download.DownloadsHandler(tools)

        self.package_name = ""
        self.endpoint = ""
        self.args = []
        self.has_custom = False
        self.service_data = {}

    def unpackage(self):
        self.tools_cs.unzipper(
            [(f"./forge/.temp/forge_{self.package_name}.zip", "./services/external/")])

    def load_service_data(self):
        service_data = self._service.get_service(self.package_name)
        self.service_data = service_data
        self.has_custom = service_data.get('custom_packages', False)
        self.endpoint = service_data.get('endpoint')

    def service_register(self):
        is_forge_package = True
        repo = self._repository.get_repository(self.package_name)
        if "my_url.com" in repo:
            is_forge_package = False

        service_data = self.tools_da.yaml_loader(
            f"./services/external/{self.package_name}/config/config.yml", "forge_service")
        service_data = service_data[0]
        self.has_custom = service_data.get('custom_packages', False)
        self.endpoint = service_data.get('endpoint')
        self._service.add_service(service_data, is_forge_package)

    def service_updater(self):
        pass

    def install_dependencies(self):
        requirements_file = f"./services/external/{self.package_name}/requirements.txt"
        try:
            with open(requirements_file, "r") as file:
                for line in file:
                    package = line.strip()
                    subprocess.check_call(["pip", "install", package])
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")

    def install_custom_packages(self):
        packages_directory = f"./emma/services/external/{self.package_name}/assets/packages"
        whl_files = glob.glob(os.path.join(packages_directory, "*.whl"))
        zip_files = glob.glob(os.path.join(packages_directory, "*.zip"))
        tar_gz_files = glob.glob(os.path.join(packages_directory, "*.tar.gz"))

        try:
            # Install .whl files
            if whl_files:
                for whl_file in whl_files:
                    try:
                        subprocess.check_call(["pip", "install", whl_file])
                    except Exception as e:
                        print(
                            f"An error occurred while trying to install whl file {e}")
                        continue

            # Install packages from .zip files using setup.py
            if zip_files:
                for zip_file in zip_files:
                    try:
                        package_directory = os.path.splitext(zip_file)[0]
                        if os.path.exists(os.path.join(package_directory, "setup.py")):
                            os.chdir(package_directory)
                            subprocess.check_call(
                                ["python", "setup.py", "install"])
                            os.chdir(packages_directory)
                    except Exception as e:
                        print(f"Error installing custom packages: {e}")

            # Install .tar.gz files
            if tar_gz_files:
                for tar_gz_file in tar_gz_files:
                    try:
                        with tarfile.open(tar_gz_file, "r:gz") as tar:
                            tar.extractall(path=packages_directory)
                        print(f"Package {tar_gz_file} extracted successfully.")

                        # Read instructions.txt file
                        instructions_file_path = os.path.join(
                            packages_directory, "instructions.txt")
                        if os.path.exists(instructions_file_path):
                            with open(instructions_file_path, "r") as instructions_file:
                                instructions = instructions_file.read()

                            # Perform installation steps
                            commands = instructions.split("\n")
                            for command in commands:
                                command = command.strip()
                                if command:
                                    try:
                                        subprocess.check_call(
                                            command, shell=True)
                                    except Exception as e:
                                        print(
                                            f"Error executing command: {command}\n{e}")
                    except Exception as e:
                        print(
                            f"Error intalling tar.gz dependencie command:\n{e}")
            # Continue with the rest of the code

        except tarfile.TarError as e:
            print(f"Error extracting package {tar_gz_file}: {e}")

            print("Custom packages installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing custom packages: {e}")

    def build(self):
        self.load_service_data()
        self.install_dependencies()
        if self.has_custom:
            self.install_custom_packages()
        # FORGE_GLOBALS().create_instance(self.package_name, self.endpoint)

    def instanciate_build(self):
        self.load_service_data()
        # FORGE_GLOBALS().create_instance(self.package_name, self.endpoint)

    def attach_components(self, module_name):
        attachable_module = __import__(module_name)

        for component_name in dir(attachable_module):
            component = getattr(attachable_module, component_name)

            if callable(component):
                self.thread_utils.attach_function(
                    self, component_name, component)
            elif isinstance(component, threading.Thread):
                self.thread_utils.attach_thread(
                    self, component_name, component)
            else:
                self.thread_utils.attach_variable(
                    self, component_name, component)

    def run(self, package_list):
        if len(package_list) == 0:
            return

        for package in package_list:
            self.package_name = package.get('package_name')
            repository = package.get('repository')

            if not all([repository, self.package_name]):
                logging.error(
                    f"{self.package_name} has Missing required parameters")
                continue

            logging.info(
                f"Known {self.package_name} package repositories: {self._repository.get_repository(self.package_name)}")

            if not self._repository.verify_repository(self.package_name):
                self._repository.add_repository(self.package_name, repository)
                key = self._download.download_package(
                    repository, self.package_name)

                if key:
                    logging.info(f"Installing {self.package_name}")
                    self.unpackage()
                    self.service_register()
                    self.build()
            else:
                if self._service.verify_service(self.package_name):
                    logging.info(f"Building {self.package_name}")
                    self.instanciate_build()
                else:
                    logging.info(f"Installing local {self.package_name}")
                    self.service_register()
                    self.instanciate_build()


# Configure logging
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    pass  # Add your application logic here
