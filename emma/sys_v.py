import datetime
import importlib
import sys
import os
import queue
import shutil
import yaml
import threading
import time
import psutil
from tools.data.local.kit import toolKit as localDataTools
from interfaces.db import Login
from cam_module import FacialRecognizer


class SystemAwake:
    def __init__(self):
        msc = importlib.import_module("emma.task_module")
        self.msc = msc.MiscellaneousModule

    def ruler(self):
        i = 0
        while i <= 3:
            rule = input("Login, register or invited?: ")
            if rule.lower() == "login":
                return self.user_login()
            elif rule.lower() == "register":
                self.user_register()
            elif rule.lower() == "invited":
                return self.invited()
            else:
                i += 1
        print("Too many intents, please try again later")
        quit()

    def user_login(self):
        i = 0
        while i <= 3:
            email = input("email: ")
            pw = input("Password: ")
            if email == " " or pw == " " or len(email) == 0 or len(pw) == 0:
                print("Some fields are empty")
                i += 1
                if i >= 3:
                    print("Too many intents please try again later")
                    quit()
            else:
                x, userData = Login.user_login(email, pw)
                if x:
                    if userData[0] == "5":
                        print("Facial Recognizer is needed for this user level")
                        if FacialRecognizer.run(userData[2], 1) == True:
                            return True
                        else:
                            return False
                    else:
                        return True
                else:
                    print("incorrect credentials")
                    i += 1
        print("Too many intents please try again later")
        quit()

    def user_register(self):
        i = 0
        while i < 3:
            user = input("Name: ")
            email = input("email: ")
            pw = input("Password: ")
            age = int(input("Age: "))
            lang = input("Lang (es/en): ")
            genre = input("genre (Male/Female): ")
            if (
                user == " "
                or email == " "
                or pw == " "
                or age == " "
                or genre == " "
                or len(user) == 0
                or len(pw) == 0
                or len(str(lang)) == 0
                or len(genre) == 0
            ):
                i += 1
                print("invalid args")
            else:
                args = [
                    FacialRecognizer.run(user, 0),
                ]
                if Login.user_register(user, email, pw, age, genre, lang, args) == True:
                    print("You has been Register")
                    print("Now Login Please")
                    self.user_login()
                else:
                    print("Error while you tryining registration")

    def run(self):
        os.environ["USERLVL"] = "3"
        os.environ["USERNAME"] = "Juan"
        os.environ["USERLANG"] = "en"
        os.environ["LOGGED"] = "True"
        bp = BackgroundProcess()
        bp.data_auto_updater()
        logged = os.environ["LOGGED"]
        os.environ["DATE"] = f"{self.msc.date_clock(2)}"
        weather = self.msc.weather("Medellin")
        dateTime = self.msc.date_clock(0)
        dayPart = self.msc.day_parts()
        text = "good {}, today is {},its {}, {}...".format(
            dayPart, dateTime[1], dateTime[2], weather
        )
        if logged == "True":
            userPrefix = Login.user_prefix()
            return userPrefix, text
        if self.ruler():
            userPrefix = Login.user_prefix()
            return userPrefix, text


class MainProcess:
    def __init__(self) -> None:
        os.environ["KNOWED_THREADS"] = [str(threading.get_ident())]
        self.listening = importlib.import_module("emma.speech._listening")
        self.web_app = importlib.import_module("web_server.app")
        self.talking = importlib.import_module("emma.speech._talking")
        self.trading = importlib.import_module("workers.trading_bots.supervisor")

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

    def server_shutdown(self):
        self.queue.get_queue("CURRENT_INPUT")
        self.console_output.write("SHUTDOWN", "DO YOU WANT TO LOG OUT?")
        time.sleep(3)
        log = self.queue.get_queue("CURRENT_INPUT")
        if log.lower() == "yes":
            self.enviroment_clearer()
        elif log.lower() == "cancel":
            return
        self.temp_clearer()
        self.remove_pycache(".")
        os._exit(0)

    def initialize_threads(
        self, config_file, queue_manager, console_manager, thread_manager
    ):
        queue = queue_manager
        console = console_manager
        thread_manager = thread_manager

        # Need some like yaml file
        with open(config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        for dic in data:
            queue.create_queue(dic["queue"], dic["queue_maxsize"])
            func_instance = getattr(dic["module"], dic["func"])
            thread = threading.Thread(
                func_instance(queue_manager, console),
                name=dic["thread_name"],
                daemon=dic["thread_is_daemon"],
            )
            thread_manager.add_thread(thread)
            if dic["autostart"]:
                thread_manager.start_thread(dic["thread_name"])

    class amy_guardian:
        def init(self) -> None:
            pass


class BackgroundProcess:
    def __init__(self, queue_manager=None, console_output=None):
        self.dM = importlib.import_module("emma.db")
        self.queue = queue_manager
        self.console_output = console_output

    def remove_pycache(self, dir_path):
        for dir_name, subdirs, files in os.walk(dir_path):
            if "__pycache__" in dir_name:
                print(f"Removing {dir_name}")
                shutil.rmtree(dir_name)
            else:
                for subdir in subdirs:
                    self.remove_pycache(os.path.join(dir_name, subdir))

    def keyboard_keybinds():
        pass

    def enviroment_clearer(self):
        clear = [
            ("USERNAME", ""),
            ("USERLVL", "1"),
            ("USERLANG", ""),
            ("LOGGED", str(False)),
        ]
        for i in clear:
            os.environ[i[0]] = i[1]

    def verify_paths(self):
        DirsStructure = [
            "./.AmyRootUser/",
            "./.AmyRootUser/.preferences",
            "./.AmyRootUser/.temp",
            "./.AmyRootUser/disk",
            "./.AmyRootUser/disk/user",
            "./.AmyRootUser/disk/apps",
            "./.AmyRootUser/disk/home/recycler",
            "./.AmyRootUser/disk/home/documents",
            "./.AmyRootUser/disk/home/music",
            "./.AmyRootUser/disk/home/pictures",
            "./.AmyRootUser/disk/home/videos",
        ]
        # Loop through the paths and verify their existence
        for path in DirsStructure:
            if not os.path.exists(path):
                # Create the directory if it doesn't exist
                os.makedirs(path)

        return "All Directories has been verified correctly"

    def data_auto_updater(self):
        self.dM.AmyData.json_task_updater()

    def temp_clearer(self):
        path = ".temp"
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
        diccionary = localDataTools.json_loader(
            "assets/json/module_directory.json", "module_dir", "dict"
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


class ThreadManager:
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

    # is broken thread should be an istance and have some issues
    def stop_thread(self, thread_name):
        self.queue.add_to_queue(f"{thread_name}_KEY", "False")
        return
        for _, thread in self.threads.items():
            current_thread = str(thread.name).split("(")[1].split(")")[0]
            if current_thread == thread_name:
                if thread.is_alive():
                    self.queue.add_to_queue(f"{current_thread.upper()}_KEY", "False")
                    return f"\n{thread_name} has been stopped."
                else:
                    return f"\n{thread_name} is not running."
        return f"\nThread '{thread_name}' not found."

    class ConsoleManager:
        def __init__(self, queue_manager):
            self.queue = queue_manager
            msc = importlib.import_module("emma.task_module")
            self.msc = msc.MiscellaneousModule
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

    class QueueManager:
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
                raise ValueError(f"No queue found with name {name}")
            if self.queues[name].maxsize == 1:
                if not self.queues[name].empty():
                    self.get_queue(name)
                self.queues[name].put(command)
            else:
                self.queues[name].put(command)

        def get_queue(self, name, out=None):
            if out != None:
                return self.queues[name].get(timeout=out)
            else:
                return self.queues[name].get()

        def remove_queue(self, name):
            if name not in self.queues:
                raise ValueError(f"No queue found with name {name}")
            del self.queues[name]


class CommandsManager:
    def __init__(self, queue_manager, console_output, thread_manager):
        self.tag = "Commands Thread"
        talk = importlib.import_module("emma.speech._talking")
        self.task = importlib.import_module("emma.task_module")
        self.local_converters = importlib.import_module("tools.converters.local.kit")
        self.local_generators = importlib.import_module("tools.generators.local.kit")
        self.local_data = importlib.import_module("tools.data.local.kit")

        self.database = importlib.import_module("emma.db")
        self.talk = talk
        self._TTS = talk._TTS()
        self.bp = BackgroundProcess(queue_manager, console_output)
        self.queue = queue_manager
        self.stop_flag = False

        self.console_output = console_output
        self.thread_manager = thread_manager
        self.modules = {
            "bp": self.bp,
            "talk": self.talk,
            "talk._TTS": self._TTS,
            "task": self.task,
            "task.MiscellaneousModule": self.task.MiscellaneousModule,
            "task.WebModule": self.task.WebModule,
            "task.OsModule": self.task.OsModule,
            "generators": self.local_generators,
            "converters": self.local_converters,
            "data": self.local_data,
            "thread": self.thread_manager,
        }
        self.run()

    def run(self):
        module = ""

        while not self.stop_flag:
            command_keyword = self.queue.get_queue("COMMANDS")

            _, args, command = self.command_indexer(command_keyword)
            if _:
                for i in self.modules.keys():
                    if command["module"] == i:
                        module = self.modules[i]
                # Execute the command
                if args != None:
                    self.execute_command(module, command["function_name"], args)
                else:
                    self.execute_command(module, command["function_name"])
            else:
                continue

    def execute_command(self, module, function_name, args=None):
        try:
            # get the function reference
            function = getattr(module, function_name)
        except Exception as e:
            self.console_output.write(self.tag, f"{e}, Cannot get Function Ref.")
            return
        # call the function
        try:
            if args == None:
                function()
            elif type(args) == int or type(args) == str:
                r = function(args)
                if r != None:
                    self.console_output.write(self.tag, r)

            self.console_output.write(self.tag, f"{function_name} has been execute")
        except Exception as e:
            self.console_output.write(
                self.tag, f"{function_name} failed or is unknown: {e}"
            )

    def command_indexer(self, command_keyword):
        args, diccionary = localDataTools.json_loader(
            "assets/json/command_directory.json",
            command_keyword,
            "command",
            self.console_output,
        )

        if diccionary != None and (type(args) == int or args == None):
            return True, args, diccionary
        elif diccionary != None and type(args) == str:
            # args = self.args_identifier(args)
            return True, args, diccionary
        else:
            return False, args, {}

    def args_identifier(self, args):
        return args

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    pass
