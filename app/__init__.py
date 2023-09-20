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
        self.tools_da, self.msc = tools
        self.establish_connections()
        self.set_environ_variables()
        self.queue_handler = queue_handler
        self.thread_manager = thread_manager
        self.system_events = system_events
        _, clock = self.msc.date_clock(2)
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
        user_file_path = "app/config/user_config.yml"
        data = self.tools_da.yaml_loader(user_file_path)

        if not data or data == {} or data == []:
            os.environ["USERLANG"] = str(input("Select a language en - es: "))
            os.environ["LOGGED"] = 'False'
            os.environ['USERNAME'] = str(input("Your Name: "))
            self.queue_handler.add_to_queue("CONSOLE",
                                            (self.name, "Setting default config"))
        else:
            os.environ["USERLANG"] = data['user']['language']
            os.environ["LOGGED"] = str(data['preferences']['stay_signed_in'])
            os.environ["USERNAME"] = data['user']['name']

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
        installed_packages = [pkg.key for pkg in pkg_resources.working_set]
        return installed_packages

    def get_missing_packages(self):
        """
        Get a list of missing packages.
        """
        installed_packages = self.get_installed_packages()
        missing_packages = [
            pkg for pkg in self.required_packages if pkg not in installed_packages]
        return missing_packages

    def install_dependencies(self, packages):
        """
        Install missing packages using pip.
        """
        for package in packages:
            subprocess.run(['pip', 'install', package], check=True)

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
