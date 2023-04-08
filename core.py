# BasePythonLibraries
from random import randint
import importlib

# Tools Libraries
from tools.data.local.kit import toolKit as localDataTools
import tools.os as sTools

from amy_basic_process.sys_v import SystemLogin, BackgroundProcess


class cluster:
    def __init__(self) -> None:
        global userPrefix
        global welcome
        # BASIC PROCESS IMPORTS
        _listen = importlib.import_module(
            'amy_basic_process.speech._listening')
        _talk = importlib.import_module(
            'amy_basic_process.speech._talking')
        self.talk = _talk.TalkProcess
        self.listen = _listen.ListenInBack
        self.dM = importlib.import_module('amy_basic_process.data_module')
        self.sys = importlib.import_module('amy_basic_process.sys_v')
        self.task = importlib.import_module('amy_basic_process.task_module')
        self.ms = importlib.import_module('amy_basic_process.miscellaneous')
        userPrefix, welcome = self.sys.awake.run()
        self.talk.talk(welcome)

    def main(self):
        global userPrefix
        input_ = self.listen.listener()
        sysA = self.sys.MainProcess
        sysB = self.sys.BackgroundProcess
        talk = self.talk.talk
        db = self.dM.AmyData
        osTask = self.task.osModule
        msc = self.ms.main
        osTools = sTools.toolKit
        data = localDataTools.string_symbol_clearer(input_)

        if data != '':
            if "amy" in data:
                data = data.replace('amy', '')
                if data == "":
                    return
                print(data)
                eAns, task, index, key = db.task_indexer(data)

                # Task
                if key == True:
                    print(data)
                    talk(eAns)
                    try:
                        eval(task)
                    except:
                        pass
                else:
                    pass
            # Chat
            chat = db.chat_indexer(data)
            if data != chat:
                print(data)
                talk(chat + userPrefix[randint(0, len(userPrefix)-1)])

    def data_auto_updater(self):
        self.dM.AmyData.json_task_updater()

    def run():
        BackgroundProcess.enviroment_clearer()
        if SystemLogin.verify():
            run = cluster()
            while True:
                run.main()
                run.data_auto_updater()
        else:
            quit()


if __name__ == '__main__':
    cluster.run()
