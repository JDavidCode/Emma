# BasePythonLibraries
import importlib
from threading import Thread
import time
# Tools Libraries


class Cluster:
    def __init__(self) -> None:
        global userPrefix
        global welcome
        # BASIC PROCESS IMPORTS
        self.sys = importlib.import_module('amy_basic_process.sys_v')
        self.listen = importlib.import_module(
            'amy_basic_process.speech._listening')
        self.trading = importlib.import_module(
            'workers.trading_bots.supervisor')
        userPrefix, welcome = self.sys.awake().run()
        self.ThreadMangement()
        self.proof()

    def ThreadMangement(self):
        thread_manager = self.sys.ThreadManager()
        # create voice thread
        voice_thread = Thread(target=self.listen.ListenInBack, daemon=True)
        thread_manager.add_thread(voice_thread)
        thread_manager.start_thread(voice_thread)  # start the voice thread
        # create Trading Bot thread
        trading_thread = Thread(target=self.trading.TradingSupervisor, daemon=True)
        thread_manager.add_thread(trading_thread)
        thread_manager.start_thread(trading_thread)

    def proof(self):
        for i in range(0, 100):
            print(i)
            time.sleep(5)


if __name__ == '__main__':
    Cluster()
