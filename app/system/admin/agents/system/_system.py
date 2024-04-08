import datetime
import os
import shutil
import time
import yaml
import threading
import psutil
import importlib
from app.config.config import Config
import traceback


class SystemAgent:
    """
    Class for managing system-related operations.

    Args:
        name (str): The name of the SystemAgent instance.
        queue_name (str): The name of the queue.
        queue_handler: An object responsible for handling the queue.
    """

    def __init__(self, name, queue_name, queue_handler=None):
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.func_instances = {}
        self.instances = {}

    def server_performance(self, threads):
        """
        Get server performance statistics.

        Args:
            threads (list): List of active threads.

        Returns:
            dict: Server performance data.
        """
        dateTime = datetime.datetime.now()
        pid = os.getpid()
        process = psutil.Process(pid)
        status = process.status()
        cpu_usage = psutil.cpu_percent()
        memory_info = process.memory_info()
        memory_usage = int(memory_info.rss / 1024.0 / 1024.0)
        server_time = process.create_time()
        server_time = datetime.datetime.fromtimestamp(server_time)
        server_time = dateTime - server_time
        server_time = int(server_time.total_seconds())
        server_time = datetime.timedelta(seconds=server_time)
        data = {
            "status": str(status),
            "cpu_usage": f"{str(cpu_usage)}%",
            "threads": str(len(threads)),
            "memory_usage": f"{str(memory_usage)} MB",
            "time": str(server_time),
        }
        return data

    def get_nested_attribute(self, obj, attribute_path):
        """
        Get a nested attribute of an object.

        Args:
            obj: The object to retrieve the attribute from.
            attribute_path (str): The path to the nested attribute.

        Returns:
            Any: The value of the nested attribute.
        """
        attributes = attribute_path.split('.')
        current_obj = obj
        for attribute in attributes:
            current_obj = getattr(current_obj, attribute)
        return current_obj

    def instance_threads(self, forge=False):
        """
        Initialize threads based on configuration data.

        Args:
            forge (bool, optional): Whether to use Forge configuration. Defaults to False.
        """
        if forge:
            config_file = "./app/config/forge_config.yml"
        else:
            config_file = "./app/config/server_config.yml"

        with open(config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        arg_mapping = {
            "queue_handler": Config.app.system.core.queue,
            "event_handler": Config.app.system.core.event,
            "thread_handler": Config.app.system.core.thread,
        }

        if forge:
            data = data["Forge"]["Threads"]
            if not data:
                return
        else:
            data = data["defaults"]["Threads"]

        for dic in data:
            if not dic:
                continue

            if "queue" in dic and dic["queue"]:
                Config.app.system.core.queue.create_queue(
                    dic["queue"], dic["queue_maxsize"])

        for dic in data:
            args = dic.get("args", [])
            if forge:
                endpoint = f"forge_package_{dic['package_name']}"
            else:
                endpoint = dic["endpoint"]

            if args:
                processed_args = [
                    dic.get("thread_name"),
                    dic.get("queue", None)
                ]

                for arg in args:
                    if arg in arg_mapping:
                        processed_args.append(arg_mapping[arg])
                    else:
                        self.queue_handler.add_to_queue(
                            "LOGGING", ("Error", f"Invalid argument: {arg}"))

                func_instance = self.get_nested_attribute(Config, endpoint)
                func_instance = func_instance(*processed_args)
                thread_name = dic.get("thread_name")
                visible = dic.get("visible", True)

                if visible and "T0" not in thread_name:
                    self.func_instances[thread_name] = func_instance

                thread_is_daemon = dic.get("thread_is_daemon", False)
                autostart = dic.get("autostart", False)
                self.initialize_thread(
                    func_instance, thread_name, autostart, thread_is_daemon)

        Config.app.thread_instances = self.func_instances

    def initialize_thread(self, func_instance, thread_name, autostart=True, thread_is_daemon=False):
        """
        Initialize and start a thread.

        Args:
            func_instance: The thread instance.
            thread_name (str): The name of the thread.
            autostart (bool, optional): Whether to start the thread immediately. Defaults to True.
            thread_is_daemon (bool, optional): Whether the thread is a daemon thread. Defaults to False.
        """
        Config.app.system.core.thread.add_thread(
            threading.Thread(
                target=lambda: func_instance.main(),
                name=thread_name,
                daemon=thread_is_daemon,
            )
        )

        if autostart:
            Config.app.system.core.thread.start_thread(thread_name)
            func_instance.run()

    def create_new_worker(self, thread_name):
        """
        Create a new worker thread based on an existing thread.

        Args:
            thread_name (str): The name of the existing thread.
        """
        if thread_name in self.func_instances:
            instance = self.func_instances[thread_name]
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, f"Worker {instance}"))

            worker_count = sum(
                1 for name in self.func_instances if name.startswith(thread_name))
            new_worker_name = f"{thread_name}_{worker_count}"
            daemon_status = Config.app.system.core.thread.get_thread_info(
                thread_name)

            self.initialize_thread(
                instance, new_worker_name, autostart=True, thread_is_daemon=daemon_status["is_daemon"])
            Config.app.thread_instances[new_worker_name] = instance
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, f"Worker {new_worker_name} has been created"))
        else:
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, f"Thread instance not found: {thread_name}"))

    def initialize_queues(self):
        """
        Initialize queues based on configuration data.
        """
        config_file = "./app/config/server_config.yml"
        queue = Config.app.system.core.queue

        with open(config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        for dic in data["defaults"]["queues"]:
            if dic is None and not isinstance(dic, str):
                continue
            if dic.get("queue") and dic.get("queue_maxsize"):
                # Handle single or multiple queue names
                queue_names = dic["queue"] if isinstance(
                    dic["queue"], list) else [dic["queue"]]

                # Handle single or multiple max sizes
                queue_maxsizes = dic["queue_maxsize"] if isinstance(
                    dic["queue_maxsize"], list) else [dic["queue_maxsize"]]

                for queue_name, queue_maxsize in zip(queue_names, queue_maxsizes):
                    queue.create_queue(queue_name, queue_maxsize)

        for dic in data["defaults"]["secure_queues"]:
            if dic is None and not isinstance(dic, str):
                continue
            if dic["queue"]:
                queue.create_secure_queue(dic["queue"], dic["queue_maxsize"])

    def recreate_reloaded_module(self, module_name):
        """
        Recreate an instance of a reloaded module.

        Args:
            module_name (str): The name of the reloaded module.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        diccionary = Config.tools.data.json_loader(
            Config.paths._globals)
        key = diccionary.keys()

        for i in key:
            if module_name in i:
                module_info = diccionary.get(i)
                endpoint = module_info.get("endpoint")
                module_path = module_info.get("path")
                args = module_info.get("args")
                isinsta = module_info.get("instance")
                args = [eval(arg) for arg in args]

                try:
                    module = importlib.import_module(module_path)

                    if eval(isinsta) and args:
                        new_instance = getattr(module, endpoint)(*args)
                    elif eval(isinsta):
                        new_instance = getattr(module, endpoint)()
                    else:
                        new_instance = getattr(module, endpoint)

                    global_namespace = globals()
                    global_namespace[module_name] = new_instance

                    return True, f"Instance {module_name} of module {module_name} has been reloaded."
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue("LOGGING", (
                        "RECREATE INSTANCE", [f"Error recreating instance of {module_name}: {e}", traceback_str]))
                    return False, traceback_str

    def server_shutdown(self, reload=False):
        """
        Shut down the server.

        Args:
            reload (bool, optional): Whether to reload the server. Defaults to False.
        """
        key = False
        timer = 0
        Config.app.system.core.event.notify_shutdown()

        while not key:
            key = Config.app.system.core.event.subscribers_shutdown_flag(
                start=True)
            time.sleep(1)
            timer += 1
            if timer >= 120:
                key = True

        Config.app.system.core.thread.kill_thread()

        for i in range(3, 0, -1):
            self.queue_handler.add_to_queue(
                "CONSOLE", (f"{self.name} SHUTDOWN", f"SERVER WILL STOP IN {i}"))
            time.sleep(1.1)

        _, val = Config.app.system.core.thread.get_thread_status()
        self.queue_handler.add_to_queue(
            "CONSOLE", (f"{self.name} SHUTDOWN", val))
        self.temp_clearer()
        self.remove_pycache(".")

        if not reload:
            os._exit(0)

    def server_restart(self):
        """
        Restart the server.
        """
        self.server_shutdown(reload=True)
        time.sleep(10)
        Config.app.app.reload()

    def remove_pycache(self, dir_path):
        """
        Remove Python cache files from a directory and its subdirectories.

        Args:
            dir_path (str): The path to the directory.
        """
        for dir_name, subdirs, files in os.walk(dir_path):
            if "__pycache__" in dir_name:
                print(f"Removing {dir_name}")
                shutil.rmtree(dir_name)
            else:
                for subdir in subdirs:
                    self.remove_pycache(os.path.join(dir_name, subdir))

    def enviroment_clearer(self):
        """
        Clear environment variables.
        """
        clear = [
            ("email", ""),
            ("USERLVL", "1"),
            ("USERLANG", ""),
            ("LOGGED", str(False)),
        ]
        for i in clear:
            os.environ[i[0]] = i[1]

    def verify_paths(self):
        """
        Verify and create directory paths if they don't exist.

        Returns:
            str: Confirmation message.
        """
        DirsStructure = [
            "./app/common/.temp",
            "./app/services/external",
        ]

        for path in DirsStructure:
            if not os.path.exists(path):
                os.makedirs(path)

        return "All Directories have been verified correctly"

    def update_database(self):
        """
        Update data automatically.
        """
        db = Config.app.system.admin.agents.db

    def temp_clearer(self):
        """
        Clear temporary files and directories.
        """
        path = "./app/common/.temp"
        if os.path.exists(path):
            for file in os.listdir(path):
                x = os.path.join(path, file)
                try:
                    os.rmdir(x)
                except Exception as e:
                    self.handle_error(e)
                try:
                    os.remove(x)
                except Exception as e:
                    self.handle_error(e)

    def module_reloader(self, module_name, is_thread=False):
        """
        Reload a module and its instance.

        Args:
            module_name (str): The name of the module to reload.
            is_thread (bool, optional): Whether the module is a thread. Defaults to False.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        queue_handler = Config.app.system.core.queue
        console_handler = Config.app.system.core._console
        thread_handler = Config.app.system.core.thread
        events_handler = Config.app.system.core.event

        try:
            if is_thread:
                config_file = "./app/config/server_config.yml"
                with open(config_file) as f:
                    data = yaml.load(f, Loader=yaml.FullLoader)
                    for dic in data["defaults"]["services"]:
                        if dic.get("thread_name") == module_name:
                            module_name = dic.get("endpoint")

            diccionary = Config.tools.data.json_loader(
                Config.paths._globals)
            key = diccionary.keys()
            reloaded = False

            for i in key:
                if module_name in i:
                    module_info = diccionary.get(i)
                    endpoint = module_info.get("endpoint")
                    path = module_info.get("path")

                    module = importlib.import_module(path)
                    importlib.reload(module)
                    importlib.invalidate_caches()

                    reloaded, message = self.recreate_reloaded_module(
                        module_name)
                    break

            if reloaded:
                return True, message
            else:
                return False, message

        except Exception as e:
            self.handle_error(e)
            return False


if __name__ == "__main__":
    pass
