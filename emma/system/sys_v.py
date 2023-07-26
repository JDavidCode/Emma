import datetime
import sys
import os
import queue
import shutil
import datetime
import yaml
import threading
import psutil
import importlib
import emma.globals as EMMA_GLOBALS


class SysV:
    def __init__(self, queue_handler=None, console_handler=None):
        self.queue = queue_handler
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

        queue = EMMA_GLOBALS.sys_v_th_qh
        console = EMMA_GLOBALS.sys_v_th_ch
        thread = EMMA_GLOBALS.sys_v_th
        system_events = EMMA_GLOBALS.sys_v_th_eh

        if forge:
            data = data["Forge"]["services"]
            if data == [] or data == None:
                return
        else:
            data = data["defaults"]["services"]

        # Define the mappings of argument combinations to function calls
        argument_mappings = {
            ("console", "queue", "system_events", "thread"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(
                console_handler=console,
                queue_handler=queue,
                system_events=system_events,
                thread_handler=thread,
            ),
            ("console", "queue", "system_events"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(
                console_handler=console,
                queue_handler=queue,
                system_events=system_events,
            ),
            ("console", "queue", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, queue_handler=queue, thread_handler=thread
            ),
            ("console", "queue"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, queue_handler=queue
            ),
            ("console", "system_events", "thread"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(
                console_handler=console,
                system_events=system_events,
                thread_handler=thread,
            ),
            ("console", "system_events"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, system_events=system_events
            ),
            ("console", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console, thread_handler=thread
            ),
            ("console",): lambda: getattr(EMMA_GLOBALS, endpoint)(
                console_handler=console
            ),
            ("queue", "system_events", "thread"): lambda: getattr(
                EMMA_GLOBALS, endpoint
            )(queue_handler=queue, system_events=system_events, thread_handler=thread),
            ("queue", "system_events"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                queue_handler=queue, system_events=system_events
            ),
            ("queue", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                queue_handler=queue, thread_handler=thread
            ),
            ("queue",): lambda: getattr(EMMA_GLOBALS, endpoint)(queue_handler=queue),
            ("system_events", "thread"): lambda: getattr(EMMA_GLOBALS, endpoint)(
                system_events=system_events, thread_handler=thread
            ),
            ("system_events",): lambda: getattr(EMMA_GLOBALS, endpoint)(
                system_events=system_events
            ),
            ("thread",): lambda: getattr(EMMA_GLOBALS, endpoint)(thread_handler=thread),
            (): lambda: getattr(EMMA_GLOBALS, endpoint)(),
        }

        for dic in data:
            if dic == {}:
                continue
            if "queue" in dic and dic["queue"] != []:
                queue.create_queue(dic["queue"], dic["queue_maxsize"])
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
        queue = EMMA_GLOBALS.sys_v_th_qh

        with open(config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        for dic in data["defaults"]["queues"]:
            if dic["queue"] != []:
                queue.create_queue(dic["queue"], dic["queue_maxsize"])

    def server_shutdown(self):
        self.console_handler.write("SHUTDOWN", "DO YOU WANT TO LOG OUT?")
        log = self.queue.get_queue("CURRENT_INPUT", 1)
        if log != None:
            if log.lower() == "yes":
                self.enviroment_clearer()
            elif log.lower() == "cancel":
                return

        EMMA_GLOBALS.sys_v_th.kill()
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
                except:
                    pass
                try:
                    os.remove(x)
                except:
                    pass

    def module_reloader(self, module_name):
        diccionary = EMMA_GLOBALS.tools_da.json_loader(
            EMMA_GLOBALS.stcpath_module_dir, "module_dir", "dict"
        )
        key = diccionary.keys()
        try:
            for i in key:
                if module_name in i:
                    module_name = diccionary.get(i)
                    importlib.reload(sys.modules[module_name])
                    print(f"module {i} has been reloaded")
                    importlib.invalidate_caches(sys.modules[module_name])
        except:
            pass


class ThreadHandler:
    def __init__(self):
        self.threads = {}

    def add_thread(self, thread):
        thread_id = id(thread)
        self.threads[thread_id] = thread

    def start_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if not thread.is_alive():
                    thread.start()
                    return f"\n{thread_name} has been started."

    def get_thread_status(self):
        status_list = []
        for _, thread in self.threads.items():
            status = thread.is_alive()
            status_list.append((thread, status))
        return status_list

    def restart_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    self.stop_thread(thread_name)
                    self.start_thread(thread_name)
                    return f"\n{thread_name} has been restarted."
                else:
                    return f"\nThread '{thread_name}' not running"
        return f"\nThread '{thread_name}' not found"

    def stop_thread(self, thread_name):
        for _, thread in self.threads.items():
            if str(thread.name) == thread_name:
                if thread.is_alive():
                    thread_instance = EMMA_GLOBALS.thread_instances.get(
                        thread_name)
                    thread_instance.stop()
                    return f"\n{thread_name} has been stopped."
                else:
                    return f"\n{thread_name} is not running."
        return f"\nThread '{thread_name}' not found."

    def kill(self):
        threads = EMMA_GLOBALS.thread_instances
        for thread_name in threads:
            for _, thread in self.threads.items():
                if str(thread.name) == thread_name:
                    if thread.is_alive():
                        thread_instance = EMMA_GLOBALS.thread_instances.get(
                            thread_name)
                        thread_instance.stop()

    class EventHandler:
        def __init__(self):
            self.subscribers = []

        def subscribe(self, subscriber):
            self.subscribers.append(subscriber)

        def notify_shutdown(self):
            for subscriber in self.subscribers:
                try:
                    subscriber.handle_shutdown()
                except Exception as e:
                    print(f"ERROR WHEN NOTIFY {subscriber} SHUTDOWN {e}")
                    continue

        def notify_overload(self):
            pass

        def notify_connection(self):
            pass

        def notify_disconnection(self):
            pass

        def notify_progress(self, progress_percentage):
            pass

    class QueueHandler:
        def __init__(self):
            self.queues = {}
            self.coutdown = 150

        def create_queue(self, name, size=None):
            if name in self.queues:
                raise ValueError(f"Queue with name {name} already exists")
            elif size != None:
                self.queues[name] = queue.Queue(maxsize=size)
            else:
                self.queues[name] = queue.Queue()

        def add_to_queue(self, name, command):
            if name not in self.queues:
                if self.coutdown >= 150:
                    print(f"No queue found with name {name}")
                    self.coutdown = 0
                else:
                    self.coutdown += 1
                return
            if self.queues[name].maxsize == 1:
                if not self.queues[name].empty():
                    _ = self.get_queue(name)
                self.queues[name].put(command)
            else:
                self.queues[name].put(command)

        def get_queue(self, name, out=None):
            if out != None:
                try:
                    return self.queues[name].get(timeout=out)
                except:
                    return None
            else:
                try:
                    return self.queues[name].get()
                except Exception as e:
                    print(e)
                    return None

        def remove_queue(self, name):
            if name not in self.queues:
                raise ValueError(f"No queue found with name {name}")
            del self.queues[name]

    class ConsoleHandler:
        def __init__(self, queue_handler):
            self.queue = queue_handler
            dateTime = datetime.datetime.now()
            clock = dateTime.time()
            self.clock = clock.strftime("%H:%M:%S")
            self.output_queue = queue.Queue()
            self.console_thread = threading.Thread(
                target=self._output_console, daemon=True
            )
            self.console_thread.start()

        def _output_console(self):
            while True:
                output = self.output_queue.get()
                self.queue.add_to_queue("CONSOLE", str(output))
                print(f"[{self.clock}] | {output}")

        def write(self, remitent, output):
            self.output_queue.put(f"{remitent}: {output}")


if __name__ == "__main__":
    pass
