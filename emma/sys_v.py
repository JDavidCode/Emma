import datetime
import sys
import os
import queue
import shutil
import yaml
import threading
import time
import psutil
import importlib
import emma.config.globals as EMMA_GLOBALS


class SystemAwake:
    def __init__(self, console_handler, queue_handler, thread_manager, system_events):
        self.console_handler = console_handler
        self.queue_handler = queue_handler
        self.thread_manager = thread_manager
        self.system_events = system_events

    def initialize_configuration(self):
        msc = EMMA_GLOBALS.task_msc
        os.environ["USERLANG"] = "en"
        os.environ["LOGGED"] = "True"
        os.environ["DATE"] = f"{msc.date_clock(2)}"
        EMMA_GLOBALS.sys_v.data_auto_updater()
        EMMA_GLOBALS.sys_v.verify_paths()
        EMMA_GLOBALS.sys_v.initialize_queues()
        EMMA_GLOBALS.sys_v.initialize_threads()

    def establish_connections(self):
        pass

    def check_dependencies(self):
        pass

    def start_services(self, package_list):
        EMMA_GLOBALS.forge_server.run(package_list)
        EMMA_GLOBALS.sys_v.initialize_threads(forge=True)

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
                "repository": "https://github.com/JDavidCode/Emma-Web_Server/releases/download/v1.0.0/web_server.zip",
                "package_name": "web_server",
            }
        ]
        self.initialize_configuration()
        self.establish_connections()
        self.check_dependencies()
        self.start_services(package_list)
        self.perform_health_checks()
        self.setup_logging()
        self.handle_errors()
        self.trigger_startup_events()

    class Auth:
        def __init__(self):
            self.max_login_attempts = 3

        def authenticate(self):
            for _ in range(self.max_login_attempts):
                option = input("Login, Register, or Invited? ").lower()

                if option == "login":
                    if self.login():
                        return
                elif option == "register":
                    self.register()
                    return
                elif option == "invited":
                    self.invited()
                    return
                else:
                    print("Invalid option. Please try again.")

            print("Too many login attempts. Please try again later.")
            quit()

        def login(self):
            for _ in range(self.max_login_attempts):
                email = input("Email: ")
                password = input("Password: ")

                if email.strip() == "" or password.strip() == "":
                    print("Some fields are empty.")
                else:
                    if self.perform_login(email, password):
                        return True
                    else:
                        print("Incorrect credentials. Please try again.")

            print("Too many login attempts. Please try again later.")
            quit()

        def perform_login(self, email, password):
            x, userData = EMMA_GLOBALS.services_db_lg.user_login(email, password)
            if x:
                if userData[0] == "5":
                    print("Facial Recognizer is needed for this user level")
                    if EMMA_GLOBALS.services_cam_fr.run(userData[2], 1):
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                return False

        def register(self):
            # Implement registration logic here
            pass

        def invited(self):
            os.environ["user_lvl"] = "1"
            os.environ["user_name"] = input("insert your name: ")
            os.environ["user_lang"] = input("select your language en/es: ")

        def logout(self):
            # Implement logout logic here
            pass


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
            if data == []:
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
            if dic["queue"] != []:
                queue.create_queue(dic["queue"], dic["queue_maxsize"])
            args = dic.get("args", [])
            if forge:
                endpoint = f"forge_package_{dic['package_name']}"
            else:
                endpoint = dic["endpoint"]

            # Find the appropriate function call based on the argument combination
            func_call = argument_mappings.get(tuple(args), argument_mappings.get(()))
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
        self.queue.get_queue("CURRENT_INPUT")
        self.console_handler.write("SHUTDOWN", "DO YOU WANT TO LOG OUT?")
        time.sleep(3)
        log = self.queue.get_queue("CURRENT_INPUT")
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
            "./emma/.EmmaRootUser/",
            "./emma/.EmmaRootUser/.preferences",
            "./emma/.EmmaRootUser/.temp",
            "./emma/.EmmaRootUser/disk",
            "./emma/.EmmaRootUser/disk/user",
            "./emma/.EmmaRootUser/disk/apps",
            "./emma/.EmmaRootUser/disk/home/recycler",
            "./emma/.EmmaRootUser/disk/home/documents",
            "./emma/.EmmaRootUser/disk/home/music",
            "./emma/.EmmaRootUser/disk/home/pictures",
            "./emma/.EmmaRootUser/disk/home/videos",
        ]
        # Loop through the paths and verify their existence
        for path in DirsStructure:
            if not os.path.exists(path):
                # Create the directory if it doesn't exist
                os.makedirs(path)

        return "All Directories has been verified correctly"

    def data_auto_updater(self):
        EMMA_GLOBALS.services_db_dt.json_task_updater()

    def temp_clearer(self):
        path = "./emma/.EmmaRootUser/.temp"
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

    def module_reloader(self, index):
        diccionary = EMMA_GLOBALS.tools_da.json_loader(
            EMMA_GLOBALS.stcpath_module_dir, "module_dir", "dict"
        )
        key = diccionary.keys()
        try:
            for i in key:
                if index in i:
                    index = diccionary.get(i)
                    print(index)
                    importlib.reload(sys.modules[index])
                    print("module", i, "has been reloaded")
                    importlib.invalidate_caches(sys.modules[index])
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
                    thread_instance = EMMA_GLOBALS.thread_instances.get(thread_name)
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
                        thread_instance = EMMA_GLOBALS.thread_instances.get(thread_name)
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

        def create_queue(self, name, size=None):
            if name in self.queues:
                raise ValueError(f"Queue with name {name} already exists")
            elif size != None:
                self.queues[name] = queue.Queue(maxsize=size)
            else:
                self.queues[name] = queue.Queue()

        def add_to_queue(self, name, command):
            if name not in self.queues:
                print(f"No queue found with name {name}")
                return
            if self.queues[name].maxsize == 1:
                if not self.queues[name].empty():
                    self.get_queue(name)
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
                return self.queues[name].get()

        def remove_queue(self, name):
            if name not in self.queues:
                raise ValueError(f"No queue found with name {name}")
            del self.queues[name]

    class ConsoleHandler:
        def __init__(self, queue_handler):
            self.queue = queue_handler
            self.msc = EMMA_GLOBALS.task_msc
            self.output_queue = queue.Queue()
            self.console_thread = threading.Thread(
                target=self._output_console, daemon=True
            )
            self.console_thread.start()

        def _output_console(self):
            while True:
                output = self.output_queue.get()
                self.queue.add_to_queue("CONSOLE", str(output))
                print(f"[{self.msc.date_clock(3)}] | {output}")

        def write(self, remitent, output):
            self.output_queue.put(f"{remitent}: {output}")


class CommandsManager:
    def __init__(self, console_handler, queue_handler, thread_handler):
        self.tag = "Commands Thread"
        self.talk = EMMA_GLOBALS.services_comunication_tg
        self.bp = SysV(queue_handler, console_handler)
        self.queue = queue_handler
        self.stop_flag = False
        self.event = threading.Event()
        self.console_handler = console_handler
        self.thread_handler = thread_handler

    def main(self):
        module = ""
        self.event.wait()
        while not self.stop_flag:
            command_keyword = self.queue.get_queue("COMMANDS")

            _, args, command = self.command_indexer(command_keyword)
            if _:
                self.queue.add_to_queue("ISTK", False)
                module = getattr(EMMA_GLOBALS, command.get("module"))
                # Execute the command
                if args != None:
                    self.execute_command(module, command.get("function_name"), args)
                else:
                    self.execute_command(module, command.get("function_name"))
            else:
                self.queue.add_to_queue("ISTK", True)
                continue

    def execute_command(self, module, function_name, args=None):
        try:
            # get the function reference
            function = getattr(module, function_name)
        except Exception as e:
            self.console_handler.write(self.tag, f"{e}, Cannot get Function Ref.")
            return
        # call the function
        try:
            if args == None:
                function()
            elif type(args) == int or type(args) == str:
                r = function(args)
                if r != None:
                    self.console_handler.write(self.tag, r)

            self.console_handler.write(self.tag, f"{function_name} has been execute")
            self.queue.add_to_queue("ISTK", False)
        except Exception as e:
            self.console_handler.write(
                self.tag, f"{function_name} failed or is unknown: {e}"
            )

    def command_indexer(self, command_keyword):
        args, diccionary = EMMA_GLOBALS.tools_da.json_loader(
            EMMA_GLOBALS.stcpath_command_dir,
            command_keyword,
            "command",
            self.console_handler,
        )

        if diccionary != None and (type(args) == int or args == None):
            return True, args, diccionary
        elif diccionary != None and type(args) == str:
            # args = self.args_identifier(args)
            return True, args, diccionary
        else:
            self.queue.add_to_queue("ISTK", True)
            return False, args, {}

    def args_identifier(self, args):
        return args

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    pass
