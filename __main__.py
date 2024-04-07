import importlib
import os
import threading
import time


class ServerIntegrityThread(threading.Thread):
    def __init__(self, thread_handler, queue_handler):
        super().__init__()
        self.stop_flag = threading.Event()
        self.thread_handler = thread_handler
        self.queue_handler = queue_handler

    def run(self):
        timer = 0
        while not self.stop_flag.is_set():
            # Your server integrity logic here

            if timer >= 1000:
                self.log_thread_status()
                timer = 0
            timer += 1
            time.sleep(1)

    def log_thread_status(self):
        key, thread_status = self.thread_handler.get_thread_status()
        for status in thread_status:
            self.queue_handler.add_to_queue(
                "CONSOLE", ("Main Thread", f"{str(status[0])} is active: {status[1]}"))


class RUN:
    def __init__(self):
        self.event = threading.Event()
        self.server_thread = None
        self.Config = None

    def reload(self):
        self.Config.del_all_sections()
        self.event.clear()
        self.run()

    def stop(self):
        if self.server_thread:
            self.server_thread.stop_flag.set()

    def initialize(self):
        # Main Server Connections, updates, corrections, etc
        init_module = importlib.import_module('app.__init__')
        self.init = init_module.Run()
        # self.init.run()
        # Server Starup
        config_module = importlib.import_module('app.config.config')
        self.Config = config_module.Config
        self.Config.auto_populate_config(config_structure)

        _, clock = self.Config.app.services.task.miscellaneous.date_clock(2)
        os.environ["DATE"] = f"{clock}"
        self.thread_handler = self.Config.app.system.core.thread
        self.queue_handler = self.Config.app.system.core.queue
        self.console_handler = self.Config.app.system.core._console
        self.event.set()
        self.Config.app._app = self

    def start_services(self, package_list):
        """
        Start application services.

        Args:
            package_list (list): List of packages to start.
        """
        self.Config.app.system.admin.agents.sys.update_database()
        self.Config.app.system.admin.agents.sys.verify_paths()
        self.Config.app.system.admin.agents.sys.initialize_queues()
        self.Config.app.system.admin.agents.sys.instance_threads()
        self.Config.inspect_config_section(self.Config.forge)
        self.Config.forge.run(package_list=package_list)
        self.Config.app.system.admin.agents.sys.instance_threads(
            forge=True)

    def run(self):
        self.initialize()
        self.start_services(package_list=[])

        self.server_thread = ServerIntegrityThread(
            self.thread_handler, self.queue_handler)
        self.server_thread.start()


config_structure = {
    "paths": {
        "#_app_dir": "app/common/json/app_directory.json",
        "#_command_dir": f"app/common/json/command_directory.json",
        "#_web_dir": "app/common/json/web_sites.json",
        "#_extensions": "app/common/json/extension.json",
        "#_command_sch": "app/common/json/command_schema.json",
        "#_globals": "app/common/json/globals.json",
    },

    "tools": {
        "@converters": "tools.converters.kit.ToolKit",
        "@generators": "tools.generators.kit.ToolKit",
        "@data": "tools.data.kit.ToolKit",
        "@network": "tools.network.ip.ToolKit"
    },

    "forge": ["forge.builder.Builder", ["FORGE", None, ['$tools.data', '$tools.converters']]],

    "app": {
        "system": {
            "core": {
                "thread": ["app.system.core._threading.ThreadHandler", ['THREAD HANDLER', None]],
                "queue": ["app.system.core._queue.QueueHandler", ['QUEUE HANDLER', None]],
                "event": ["app.system.core._event.EventHandler", ['EVENT HANDLER', None, '$app.system.core.queue']],
                "@_console": "app.system.core._console.Console",
                "@_logger": "app.system.core.logging.logger.Logger",
            },

            "admin": {
                "agents": {
                    "@withelist": ["app.system.admin.agents.system._withelist.WhitelistAgent"],
                    "sys": ["app.system.admin.agents.system._system.SystemManager", ['SYS AGENT', None, '$app.system.core.queue']],
                    "db": ["app.system.admin.agents.database._db.Database", ["DATABASE", "$app.system.core.queue"]],
                    "user": ["app.system.admin.agents.user._usr.UserManager", ["USER AGENT"]],
                    "session": ["app.system.admin.agents.sessions._sessions.SessionsAgent", ["SESSIONS AGENT", '$app.system.core.queue', '$app.system.core.event']]

                },
                "routers": {
                    "@_input": "app.system.admin.routers._input.InputRouter",
                    "@_command": "app.system.admin.routers._command.CommandRouter"
                },
                "protocols": {
                },
            },

            "thread_instances": {},  # change on runing,
            "_app": None  # reference to the complete app should be change the value on runing
        },



        "services": {
            "api": {
                "@web_api": "app.services.api.web.app.App",
                "@telegram_api": "app.services.api.telegram.app.App",
                # "@api_streaming": "app.services.api.streaming.app.App",
            },
            "external": {"@gpt": "app.services.external.gpt.GPT",
                         "@aidoc_reader": "app.services.external.aidoc_reader.AIDOC_READER",
                         },
            "task": {
                "miscellaneous": ["app.services.task.miscellaneous.MiscellaneousTask", []],
                "ost": ["app.services.task.ost.OsTask", []],
                "web": ["app.services.task.web.WebTask", []]
            },
            "common": {
            }
        },
    },
}


if __name__ == "__main__":
    run_instance = RUN()
    run_instance.run()
