# BasePythonLibraries
import importlib
from threading import Thread
import time
# Tools Libraries


class Cluster:

    def __init__(self) -> None:
        global userPrefix
        # BASIC PROCESS IMPORTS
        self.sys = importlib.import_module('amy_basic_process.sys_v')
        self.listening = importlib.import_module(
            'amy_basic_process.speech._listening')
        self.talking = importlib.import_module(
            'amy_basic_process.speech._talking')
        self.trading = importlib.import_module(
            'workers.trading_bots.supervisor')
        userPrefix, welcome = self.sys.awake().run()
        self.thread_manager = self.sys.ThreadManager()
        self.console_manager = self.thread_manager.ConsoleManager()
        self.queue_manager = self.thread_manager.QueueManager()
        self.ThreadMangement()
        self.keep_runing()

    def ThreadMangement(self):
        thread_manager = self.thread_manager
        queue_manager = self.queue_manager
        console_manager = self.console_manager

        # create a Queue for COMMANDS
        queue_manager.create_queue("COMMANDS")
        # create a Queue for TALKING
        queue_manager.create_queue("TALKING")

        # create CommandManager thread
        CommandManager = Thread(target=self.sys.CommandsManager, args=[
                                queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(CommandManager)
        # start the CommandManager thread
        thread_manager.start_thread(CommandManager)

        # create listening thread
        voice_thread = Thread(target=self.listening.ListenInBack,
                              args=[queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(voice_thread)
        thread_manager.start_thread(voice_thread)  # start  listening thread

        # create talking thread
        talk_thread = Thread(target=self.talking.Talk,
                             args=[queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(talk_thread)
        thread_manager.start_thread(talk_thread)  # start  talking thread

        # create Trading Bot thread
        trading_thread = Thread(
            target=self.trading.TradingSupervisor, args=[console_manager], daemon=True)
        thread_manager.add_thread(trading_thread)
        thread_manager.start_thread(trading_thread)  # start  Trading thread

    def keep_runing(self):
        # Define a list to hold tasks
        tasks = []

        while True:
            if len(tasks) > 0:
                # Do something with the tasks
                print("Processing tasks:", tasks)
                tasks = []
            else:
                # Sleep for a certain period of time before checking again
                self.console_manager.write(
                    "Main Thread", self.thread_manager.get_threads())
                time.sleep(900)


if __name__ == '__main__':
    Cluster()
