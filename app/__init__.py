import os
import pkg_resources
import subprocess
from app.config.config import Config


class Run:
    """
    this class for initializing the application and starting services.

    Args:
        name (str): The name of this instance.
        queue_name (str): The name of the queue.
        queue_handler: An object responsible for handling the queue.
        thread_manager: An object responsible for managing threads.
        system_events: An object for managing system events.
        tools (list, optional): Additional tools to use. Defaults to an empty list.
    """

    def __init__(self, name, queue_name, queue_handler, thread_manager, system_events, tools=[]):
        self.name = name
        self.queue_name = queue_name
        self.required_packages = [
            'pywhatkit',
            'pygame',
            'Pandas',
            'NumPy',
            'matplotlib',
            'opencv-python',
            'pywhatkit',
            'opencv-contrib-python',
            'youtube-dl',
            'PyAutoGUI',
            'mysql-connector-python',
            'imutils',
            'pyyaml',
            'img2pdf',
            'psutil',
            'openai',
            'pyatv',
            'flask-socketio',
            'Flask',
            'geopy',
            'selenium',
            'chromedriver_autoinstaller',
            'Panda3D',
            'mplfinance',
            'keyboard',
            'Pillow'
        ]
        self.tools_da, self.miscellaneous = tools
        self.establish_connections()
        self.set_environ_variables()
        self.queue_handler = queue_handler
        self.thread_manager = thread_manager
        self.system_events = system_events
        _, clock = self.miscellaneous.date_clock(2)
        os.environ["DATE"] = f"{clock}"

    def establish_connections(self):
        """
        Establish connections required for the application.
        """
        Config.app.system.admin.agents.sys.update_database()
        pass

    def set_environ_variables(self):
        """
        Set environment variables based on user configuration.
        """
        pass

    def initialize_configuration(self):
        """
        Initialize the application's configuration.
        """
        # self.check_dependencies()

        Config.app.system.admin.agents.sys.verify_paths()
        Config.app.system.admin.agents.sys.initialize_queues()
        Config.app.system.admin.agents.sys.instance_threads()

    def check_dependencies(self):
        """
        Check and handle application dependencies.
        """
        missing_packages = self.get_missing_packages()

        if missing_packages:
            print("Missing dependencies. Installing...")
            self.install_dependencies(missing_packages)
            print("Dependencies installed.")
        else:
            print("All dependencies are met.")

    def get_installed_packages(self):
        """
        Get a list of installed packages.
        """
        installed_packages = [pkg.project_name.lower()
                              for pkg in pkg_resources.working_set]
        return installed_packages

    def get_missing_packages(self):
        """
        Get a list of missing packages.
        """
        installed_packages = self.get_installed_packages()
        missing_packages = [
            pkg for pkg in self.required_packages if pkg.lower() not in installed_packages
        ]
        return missing_packages

    def install_dependencies(self, packages):
        """
        Install missing packages using pip.
        """
        try:
            # Verifica la versión de pip y actualiza si es necesario
            subprocess.run('pip install --upgrade pip', shell=True, check=True)

            for package in packages:
                # Verifica si el paquete ya está instalado
                if not self.is_package_installed(package):
                    print(f"Installing {package}...")
                    subprocess.run(
                        f'pip install {package}', shell=True, check=True)
                else:
                    print(f"{package} is already installed.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def is_package_installed(self, package):
        """
        Verifica si un paquete está instalado.
        """
        try:
            subprocess.run(f'pip show {package}', shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def start_services(self, package_list):
        """
        Start application services.

        Args:
            package_list (list): List of packages to start.
        """
        Config.inspect_config_section(Config.forge)
        Config.forge.run(package_list=package_list)
        Config.app.system.admin.agents.sys.instance_threads(forge=True)

    def perform_health_checks(self):
        """
        Perform health checks for the application.
        """
        pass

    def setup_logging(self):
        """
        Set up logging for the application.
        """
        pass

    def handle_errors(self):
        """
        Handle errors and exceptions in the application.
        """
        pass

    def trigger_startup_events(self):
        """
        Trigger startup events for the application.
        """
        pass

    def run(self):
        """
        Run the application startup process.
        """
        package_list = [
            {
                "repository": "https://github.com/ItsMaper/Emma-Trading_Bots/releases/download/v1.0.0/trading_bots.zip",
                "package_name": "trading_bots",
            }
        ]
        self.initialize_configuration()
        self.establish_connections()
        self.check_dependencies()
        self.start_services(package_list=[])
        self.perform_health_checks()
        self.setup_logging()
        self.handle_errors()
        self.trigger_startup_events()
