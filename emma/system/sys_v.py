import datetime
import sys
import os
import shutil
import time
import yaml
import threading
import psutil
import importlib
import emma.globals as EMMA_GLOBALS
import traceback

class SysV:
    def __init__(self, queue_handler=None, console_handler=None):
        self.queue_handler = queue_handler
        self.console_handler = console_handler

    def server_performance(self, threads):
        dateTime = datetime.datetime.now()
        # Get the process details of the Python app
        pid = os.getpid()
        process = psutil.Process(pid)
        # Get the memory usage of the Python app
        status = process.status()
        cpu_usage = psutil.cpu_percent()
        memory_info = process.memory_info()
        # Convert from bytes to MB
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

    def initialize_threads(self, forge=False):
        if forge:
            config_file = "emma/config/forge_config.yml"
        else:
            config_file = "emma/config/server_config.yml"
        with open(config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        func_instances = {}

        queue = EMMA_GLOBALS.core_queue_handler
        console = EMMA_GLOBALS.core_console_handler
        thread = EMMA_GLOBALS.core_thread_handler
        events = EMMA_GLOBALS.core_event_handler

        if forge:
            data = data["Forge"]["services"]
            if data == [] or data == None:
                return
        else:
            data = data["defaults"]["services"]

        # Define the mappings of argument combinations to function calls
        argument_mappings = {
            ("console", "queue", "events", "thread"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(
                console_handler=console,
                queue_handler=queue,
                event_handler=events,
                thread_handler=thread,
            ),
            ("console", "queue", "events"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(
                console_handler=console,
                queue_handler=queue,
                event_handler=events,
            ),
            ("console", "queue", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, queue_handler=queue, thread_handler=thread
            ),
            ("console", "queue"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, queue_handler=queue
            ),
            ("console", "events", "thread"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(
                console_handler=console,
                event_handler=events,
                thread_handler=thread,
            ),
            ("console", "events"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, event_handler=events
            ),
            ("console", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, thread_handler=thread
            ),
            ("console",): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console
            ),
            ("queue", "events", "thread"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(queue_handler=queue, event_handler=events, thread_handler=thread),
            ("queue", "events"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                queue_handler=queue, event_handler=events
            ),
            ("queue", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                queue_handler=queue, thread_handler=thread
            ),
            ("queue",): lambda: getattr(EMMA_GLOBALS, endpoint)(queue_handler=queue),
            ("events", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                event_handler=events, thread_handler=thread
            ),
            ("events",): lambda: getattr(EMMA_GLOBALS, endpoint)(
                event_handler=events
            ),
            ("thread",): lambda: getattr(EMMA_GLOBALS, endpoint)(thread_handler=thread),
            (): lambda: getattr(EMMA_GLOBALS, endpoint)()
        }

        for dic in data:
            if dic == {}:
                continue
            if "queue" in dic and dic["queue"] != []:
                queue.create_queue(dic["queue"], dic["queue_maxsize"])
                
        for dic in data:   
            args = dic.get("args", [])
            if forge:
                endpoint = f"forge_package_{dic['package_name']}"
            else:
                endpoint = dic["endpoint"]

            # Find the appropriate function call based on the argument combination
            func_call = argument_mappings.get(
                tuple(args), argument_mappings.get(()))
            func_instance = func_call()  # Call the function to get the instance

            func_instances[dic["thread_name"]] = func_instance

            thread_name = dic.get("thread_name")
            thread_is_daemon = dic.get("thread_is_daemon", False)
            autostart = dic.get("autostart", False)

            thread.add_thread(
                threading.Thread(
                    target=lambda: func_instance.main(),
                    name=thread_name,
                    daemon=thread_is_daemon,
                )
            )

            if autostart:
                thread.start_thread(thread_name)
                func_instance.run()
                
        EMMA_GLOBALS.thread_instances = func_instances

    def initialize_queues(self):
        config_file = "emma/config/server_config.yml"
        queue = EMMA_GLOBALS.core_queue_handler

        with open(config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        for dic in data["defaults"]["queues"]:
            if dic["queue"] != []:
                queue.create_queue(dic["queue"], dic["queue_maxsize"])
        for dic in data["defaults"]["secure_queues"]:
            if dic["queue"] != []:
                queue.create_secure_queue(dic["queue"], dic["queue_maxsize"])

    def server_shutdown(self):       
        key= False
        timer = 0
        EMMA_GLOBALS.core_event_handler.notify_shutdown()
        while not key:
            key = EMMA_GLOBALS.core_event_handler.subscribers_shutdown_flag(start=True)
            time.sleep(1)
            timer+=1
            if timer >= 120:
                key = True
        EMMA_GLOBALS.core_thread_handler.kill_thread()
        
        for i in range(7, 0, -1):
            self.console_handler.write("SYS SHUTDOWN", f"SERVER WILL STOP IN {i}")
            time.sleep(1.1)

        _, val = EMMA_GLOBALS.core_thread_handler.get_thread_status()
        self.console_handler.write("SYS SHUTDOWN", val)
        self.temp_clearer()
        self.remove_pycache("./emma")
        os._exit(0)

    def remove_pycache(self, dir_path):
        for dir_name, subdirs, files in os.walk(dir_path):
            if "__pycache__" in dir_name:
                print(f"Removing {dir_name}")
                shutil.rmtree(dir_name)
            else:
                for subdir in subdirs:
                    self.remove_pycache(os.path.join(dir_name, subdir))

    def keyboard_keybinds(self):
        pass

    def enviroment_clearer(self):
        clear = [
            ("email", ""),
            ("USERLVL", "1"),
            ("USERLANG", ""),
            ("LOGGED", str(False)),
        ]
        for i in clear:
            os.environ[i[0]] = i[1]

    def verify_paths(self):
        DirsStructure = [
            "./emma/common/.temp",
            "./emma/services/external",

        ]
        # Loop through the paths and verify their existence
        for path in DirsStructure:
            if not os.path.exists(path):
                # Create the directory if it doesn't exist
                os.makedirs(path)

        return "All Directories has been verified correctly"

    def data_auto_updater(self):
        EMMA_GLOBALS.services_db  # request

    def temp_clearer(self):
        path = "./emma/common/.temp"
        if os.path.exists(path):
            for file in os.listdir(path):
                x = path + "/" + file
                try:
                    os.rmdir(x)
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue("LOGGING", ("SYS V",(e, traceback_str)))
                try:
                    os.remove(x)
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue("LOGGING", ("SYS V",(e, traceback_str)))
                    

    def module_reloader(self, module_name, is_thread=False):
        try:
            if is_thread:
                config_file = "emma/config/server_config.yml"
                with open(config_file) as f:
                    data = yaml.load(f, Loader=yaml.FullLoader)
                    for dic in data["defaults"]["services"]:
                        if dic.get("thread_name") == module_name:
                            module_name = dic.get("endpoint")

            diccionary = EMMA_GLOBALS.tools_da.json_loader(
                EMMA_GLOBALS.stcpath_globals)
            key = diccionary.keys()
            reloaded = False

            for i in key:
                if module_name in i:
                    module_info = diccionary.get(i)
                    endpoint = module_info.get("endpoint")
                    path = module_info.get("path")


                    # Reload the module
                    module = importlib.import_module(path)
                    importlib.reload(module)
                    importlib.invalidate_caches()

                    reloaded, message= EMMA_GLOBALS.recreate_reloaded_module(module_name)
                    break

            if reloaded:
                return True, message
            else:
                return False, message
            
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", ("SYS V", (e, traceback_str)))
            return False, traceback_str



if __name__ == "__main__":
    pass
