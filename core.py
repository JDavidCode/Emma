# BasePythonLibraries
from concurrent.futures import ThreadPoolExecutor
from random import randint
import importlib

# Tools Libraries
import tools.data as dataTools
import tools.os as sTools

from amy_basic_process.login import systemLogin

userPrefix = []


class Run:
    def __init__(self) -> None:
        # BASIC PROCESS IMPORTS
        self.awake = importlib.import_module('amy_basic_process.awake')
        self.vM = importlib.import_module('amy_basic_process.voice_module')
        self.dM = importlib.import_module('amy_basic_process.data_module')
        self.sys = importlib.import_module('amy_basic_process.sys')
        self.task = importlib.import_module('amy_basic_process.task_module')
        self.ms = importlib.import_module('amy_basic_process.miscellaneous')

    def main(self):
        global userPrefix
        input_ = self.vM.ListenInBack.Listener()
        sysA = self.sys.mainProcess
        sysB = self.sys.backgroundProcess
        talk = self.vM.talkProcess.talk
        db = self.dM.AmyData
        osTask = self.task.osModule
        msc = self.ms.main
        dTools = dataTools.toolKit
        osTools = sTools.toolKit

        data = dTools.strClearerSymbol(input_)

        if data != '':
            if "amy" in data:
                data = data.replace('amy', '')
                eAns, task, index, key = db.taskIndexer(data)

                # Task
                if key == True:
                    print(data)
                    talk(eAns)
                    eval(task)
                else:
                    pass
            # Chat
            chat = db.chatIndexer(data)
            if data != chat:
                print(data)
                talk(chat + userPrefix[randint(0, len(userPrefix)-1)])

    def firstRun(self):
        self.awake.awake.run()

    def prefix(self):
        global userPrefix
        userPrefix = self.dM.login.userPrefix()

    def dataAutoUpdater(self):
        self.dM.AmyData.jsonTaskUpdater()


if __name__ == '__main__':
    worker = ThreadPoolExecutor(max_workers=4)
    backWorker = ThreadPoolExecutor(max_workers=8)
    if systemLogin.verify():
        run = Run()
        run.firstRun()
        run.prefix()
        while True:
            worker.submit(run.main())
            backWorker.submit(run.dataAutoUpdater())
    else:
        quit()
