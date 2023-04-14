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
        self.listen = importlib.import_module(
            'amy_basic_process.speech._listening')
        self.trading = importlib.import_module(
            'workers.trading_bots.supervisor')
        userPrefix, welcome = self.sys.awake().run()
        self.ThreadMangement()
        self.keep_runing()

    def ThreadMangement(self):
        thread_manager = self.sys.ThreadManager()
        queue_manager = thread_manager.QueueManager()
        console_manager = thread_manager.ConsoleManager()

        # create a Queue for COMMANDS
        queue_manager.create_queue("COMMANDS")
        # create CommandManager thread
        CommandManager = Thread(target=self.sys.CommandsManager, args=[
                                queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(CommandManager)
        # start the CommandManager thread
        thread_manager.start_thread(CommandManager)

        # create voice thread
        voice_thread = Thread(target=self.listen.ListenInBack,
                              args=[queue_manager, console_manager], daemon=True)
        thread_manager.add_thread(voice_thread)
        thread_manager.start_thread(voice_thread)  # start the voice thread

        # create Trading Bot thread
        trading_thread = Thread(
            target=self.trading.TradingSupervisor, args=[console_manager], daemon=True)
        thread_manager.add_thread(trading_thread)
        thread_manager.start_thread(trading_thread)  # start the Trading thread

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
                time.sleep(5)


if __name__ == '__main__':
    Cluster()
