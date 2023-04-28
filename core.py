# BasePythonLibraries
import importlib
from threading import Thread
import time
from web_server import app as web_app


class Cluster:

    def __init__(self) -> None:
        # self.packages_integrity = importlib.import_module('setup')
        # self.packages_integrity.PackageInstaller()
        # BASIC PROCESS IMPORTS
        self.sys = importlib.import_module('amy_basic_process.sys_v')
        self.listening = importlib.import_module(
            'amy_basic_process.speech._listening')
        self.talking = importlib.import_module(
            'amy_basic_process.speech._talking')
        self.trading = importlib.import_module(
            'workers.trading_bots.supervisor')
        self.web_app = web_app
        userPrefix, welcome = self.sys.awake().run()
        self.thread_manager = self.sys.ThreadManager()
        self.queue_manager = self.thread_manager.QueueManager()
        self.console_manager = self.thread_manager.ConsoleManager(
            self.queue_manager)
        self.ThreadMangement()
        self.ServerIntegrity()

    def ThreadMangement(self):
        thread_manager = self.thread_manager
        queue_manager = self.queue_manager
        console_manager = self.console_manager

        # Create a Queue for CURRENTS
        queue_manager.create_queue("CURRENT_INPUT", 1)
        # Create a Queue for CONSOLE
        queue_manager.create_queue("CONSOLE")
        # create a Queue for COMMANDS
        queue_manager.create_queue("COMMANDS")
        # create a Queue for TALKING
        queue_manager.create_queue("TALKING")
        # Create a Queue for WBDATA
        queue_manager.create_queue("SERVERDATA", 1)

        # create CommandManager thread
        CommandManager = Thread(target=self.sys.CommandsManager, args=[
                                queue_manager, console_manager, thread_manager], daemon=True)
        thread_manager.add_thread(CommandManager)
        # start the CommandManager thread
        thread_manager.start_thread("CommandsManager")

        # create listening thread
        voice_thread = Thread(target=self.listening.ListenInBack,
                              args=[queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(voice_thread)
        # thread_manager.start_thread("ListenInBack")  # start  listening thread

        # create talking thread
        talk_thread = Thread(target=self.talking.Talk,
                             args=[queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(talk_thread)
        thread_manager.start_thread("Talk")  # start  talking thread

        # create CommandManager thread
        web_app_thread = Thread(target=self.web_app.WebApp, args=[
                                queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(web_app_thread)
        # start the CommandManager thread
        thread_manager.start_thread("WebApp")

        # create Trading Bot thread
        trading_thread = Thread(
            target=self.trading.TradingSupervisor, args=[console_manager], daemon=True)
        thread_manager.add_thread(trading_thread)
        # thread_manager.start_thread("TradingSupervisor")  # start  Trading thread
        time.sleep(3)

    def ServerIntegrity(self):
        timer = 9000
        mp = self.sys.MainProcess()
        while True:
            json = mp.server_performance(
                self.thread_manager.get_thread_status())
            self.queue_manager.add_to_queue("SERVERDATA", json)
            if timer >= 8990:
                # Sleep for a certain period of time before checking again
                thread_status = self.thread_manager.get_thread_status()
                for status in thread_status:
                    self.console_manager.write("Main Thread",
                                               "{} is active: {}".format(str(status[0]), status[1]))
                timer = 0
            timer += 1
            time.sleep(1)


if __name__ == '__main__':
    Cluster()
