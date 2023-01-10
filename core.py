# BasePythonLibraries
from random import randint
import importlib

# Tools Libraries
from tools.data.local.kit import toolKit as localDataTools
import tools.os as sTools

from amy_basic_process.sys import systemLogin, backgroundProcess


class cluster:
    def __init__(self) -> None:
        # BASIC PROCESS IMPORTS
        self.awake = importlib.import_module('amy_basic_process.awake')
        self.vM = importlib.import_module('amy_basic_process.voice_module')
        self.dM = importlib.import_module('amy_basic_process.data_module')
        self.sys = importlib.import_module('amy_basic_process.sys')
        self.task = importlib.import_module('amy_basic_process.task_module')
        self.ms = importlib.import_module('amy_basic_process.miscellaneous')
        global userPrefix
        userPrefix = self.awake.awake.run()

    def main(self):
        global userPrefix
        input_ = self.vM.ListenInBack.Listener()
        sysA = self.sys.mainProcess
        sysB = self.sys.backgroundProcess
        talk = self.vM.talkProcess.talk
        db = self.dM.AmyData
        osTask = self.task.osModule
        msc = self.ms.main
        osTools = sTools.toolKit

        data = localDataTools.strClearerSymbol(input_)

        if data != '':
            if "amy" in data:
                data = data.replace('amy', '')
                eAns, task, index, key = db.taskIndexer(data)

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
            chat = db.chatIndexer(data)
            if data != chat:
                print(data)
                talk(chat + userPrefix[randint(0, len(userPrefix)-1)])

    def dataAutoUpdater(self):
        self.dM.AmyData.jsonTaskUpdater()

    def run():
        backgroundProcess.envClearer()
        if systemLogin.verify():
            run = cluster()
            while True:
                run.main()
                run.dataAutoUpdater()
        else:
            quit()


if __name__ == '__main__':
    cluster.run()
