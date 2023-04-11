import importlib
import sys
import os
import multiprocessing
import queue
import threading
from dotenv import set_key
from tools.data.local.kit import toolKit as localDataTools
from amy_basic_process.data_module import Login
from amy_basic_process.cam_module import FacialRecognizer


class awake:
    def __init__(self):
        msc = importlib.import_module("amy_basic_process.task_module")
        self.msc = msc.MiscellaneousModule

    def run(self):
        bp = BackgroundProcess()
        bp.enviroment_clearer()
        bp.data_auto_updater()
        if SystemLogin().ruler():
            userPrefix = Login.user_prefix()
            weather = self.msc.weather('Medellin')
            dateTime = self.msc.date_clock(0)
            dayPart = self.msc.day_parts()
            text = 'good {}, today is {},its {}, {}'.format(
                dayPart, dateTime[1], dateTime[2], weather)
            return userPrefix, text


class SystemLogin():
    def __init__(self) -> None:
        pass

    def ruler(self):
        i = 0
        while i <= 3:
            rule = input('Login, register or invited?: ')
            if rule == 'Login' or rule == 'login':
                return self.user_login()
            elif rule == 'Register' or rule == 'register':
                self.user_register()
            elif rule == 'Invited' or rule == "invited":
                return self.invited()
            else:
                i += 1
        print("Too many intents, please try again later")
        quit()

    def user_login(self):
        i = 0
        while i <= 3:
            email = input('email: ')
            pw = input('Password: ')
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
                        print('Facial Recognizer is needed for this user level')
                        if (FacialRecognizer.run(userData[2], 1) == True):
                            return True
                        else:
                            return False
                    else:
                        return True
                else:
                    print('incorrect credentials')
                    i += 1
        print("Too many intents please try again later")
        quit()

    def user_register(self):
        i = 0
        while i < 3:
            user = input('Name: ')
            email = input('email: ')
            pw = input('Password: ')
            age = int(input('Age: '))
            lang = input('Lang (es/en): ')
            genre = input('genre (Male/Female): ')
            if user == " " or email == " " or pw == " " or age == " " or genre == " " or len(user) == 0 or len(pw) == 0 or len(str(lang)) == 0 or len(genre) == 0:
                i += 1
                print("invalid data")
            else:

                data = [FacialRecognizer.run(user, 0), ]
                if Login.user_register(user, email, pw, age, genre, lang, data) == True:
                    print('You has been Register')
                    print('Now Login Please')
                    self.user_login()
                else:
                    print("Error while you tryining registration")


class ThreadManager:
    def __init__(self):
        self.threads = {}

    def add_thread(self, thread):
        thread_id = id(thread)
        self.threads[thread_id] = thread

    def start_thread(self, thread):
        thread.start()

    def stop_thread(self, thread):
        thread_id = id(thread)
        if thread_id in self.threads:
            del self.threads[thread_id]
            thread.join()

    def pause_thread(self, thread):
        # implement pause functionality as needed
        pass

    def resume_thread(self, thread):
        # implement resume functionality as needed
        pass

    def kill_threads(self):
        for thread in self.threads:
            thread.stop()

    class ConsoleOutput:
        def __init__(self):
            self.output_queue = queue.Queue()
            self.console_thread = threading.Thread(
                target=self._output_console, daemon=True)
            self.console_thread.start()

        def _output_console(self):
            while True:
                output = self.output_queue.get()
                print(output)

        def write(self, output):
            self.output_queue.put(output)


class MainProcess:
    def __init__(self) -> None:
        pass


class BackgroundProcess:
    def __init__(self) -> None:
        self.dM = importlib.import_module("amy_basic_process.data_module")

    def server_shutdown(self):
        ThreadManager().kill_threads()
        self.temp_clearer()
        self.remove_pycache('.')
        self.enviroment_clearer()
        os._exit(0)

    def amy_guardian():
        pass

    def remove_pycache(self, dir_path):
        for dir_name, subdirs, files in os.walk(dir_path):
            if '__pycache__' in dir_name:
                print(f"Removing {dir_name}")
                os.rmdir(dir_name)
            else:
                for subdir in subdirs:
                    self.remove_pycache(os.path.join(dir_name, subdir))

    def keyboard_keybinds():
        pass

    def enviroment_clearer(self):
        clear = [('USERNAME', ''), ('USERLVL', '1'), ('USERLANG', '')]
        for i in clear:
            set_key(".venv/.env", i[0], i[1])

    def verify_paths(self):
        pass

    def data_auto_updater(self):
        self.dM.AmyData.json_task_updater()

    def temp_clearer(self):
        path = '.temp'
        for file in os.listdir(path):
            x = path+'\\'+file
            try:
                os.rmdir(x)
            except:
                pass
            try:
                os.remove(x)
            except:
                pass

    def module_reloader(self, index):
        json_type = 'dict'
        diccionary = localDataTools.json_loader(
            "assets\\json\\module_directory.json", json_type, "moduleDirectory")
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

    def global_variables_setter():
        pass


class CommandsManager:
    def __init__(self, _task, data):
        talk = importlib.import_module('amy_basic_process.speech._talking')
        self.task = importlib.import_module('amy_basic_process.task_module')
        self.dm = importlib.import_module('amy_basic_process.data_module')
        self.talk = talk.TalkProcess
        self.bp = BackgroundProcess()
        self._task = _task
        self.data = data
        self.run()

    def run(self):
        index = self.data
        try:
            eval(self._task)
        except Exception as e:
            print(e)
            return


if __name__ == '__main__':
    pass
