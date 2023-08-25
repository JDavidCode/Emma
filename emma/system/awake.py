
import os
from emma.config.config import Config


class SystemAwake:
    def __init__(self, name, queue_name, queue_handler, thread_manager, system_events, tools=[]):
        self.name = name
        self.queue_name = queue_name
        self.tools_da, self.msc = tools
        self.establish_connections()
        self.set_environ_variables()
        self.queue_handler = queue_handler
        self.thread_manager = thread_manager
        self.system_events = system_events
        _, clock = self.msc.date_clock(2)
        os.environ["DATE"] = f"{clock}"

    def establish_connections(self):
        pass

    def set_environ_variables(self):
        user_file_path = "./emma/config/user_config.yml"
        data = self.tools_da.yaml_loader(user_file_path)
        if data == {} or data == [] or data == None:
            os.environ["USERLANG"] = str(input("Select a language en - es"))
            os.environ["LOGGED"] = 'False'
            os.environ['USERNAME'] = str(input("Your Name"))
            self.queue_handler.add_to_queue("CONSOLE",
                                            (self.name, "Setting default config"))
        else:
            os.environ["USERLANG"] = data['user']['language']
            os.environ["LOGGED"] = str(data['preferences']['stay_signed_in'])
            os.environ["USERNAME"] = data['user']['name']

    def initialize_configuration(self):
        Config.system.core.sys_variations.data_auto_updater()
        Config.system.core.sys_variations.verify_paths()
        Config.system.core.sys_variations.initialize_queues()
        Config.system.core.sys_variations.instance_threads()

    def check_dependencies(self):
        pass

    def start_services(self, package_list):
        Config.inspect_config_section(Config.system.forge)
        Config.system.forge.run(package_list=package_list)
        Config.system.core.sys_variations.instance_threads(forge=True)

    def perform_health_checks(self):
        pass

    def setup_logging(self):
        pass

    def handle_errors(self):
        pass

    def trigger_startup_events(self):
        pass

    def run(self):
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
