import glob
import importlib
import os
import tarfile
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
        is_forge_package = True
        repo = self._repository.get_repository(self.package_name)
        if "my_url.com" in repo.values():
            is_forge_package = False

        service_data = self.tools_da.yaml_loader(
            f"./emma/services/external/{self.package_name}/config/config.yml", "forge_service")
        service_data = service_data[0]
        self.has_custom = service_data.get('custom_packages', False)
        self.endpoint = service_data.get('endpoint')
        self._service.add_service(service_data, is_forge_package)

    def service_updater(self):
        pass

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
        FORGE_GLOBALS().create_instance(self.package_name, self.endpoint)

    def instanciate_build(self):
        self.load_service_data()
        FORGE_GLOBALS().create_instance(self.package_name, self.endpoint)

    def run(self, package_list):
        if len(package_list) == 0:
            return
        for package in package_list:
            self.package_name = package.get('package_name')
            repository = package.get('repository')
            print(f"Forge Builder is installing {self.package_name}...")
            if not all([repository, self.package_name]):
                print(f"{self.package_name} has Missing required parameters")
                continue

            print(f"Known {self.package_name} package repositories:",
                  self._repository.get_repository(self.package_name))
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
                    self.instanciate_build()
                else:
                    print(f"Installing local {self.package_name}")
                    self.service_register()
                    self.instanciate_build()
                continue
