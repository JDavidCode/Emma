# BasePythonLibraries
from concurrent.futures import ThreadPoolExecutor
from random import randint
import importlib

# Tools Libraries
import amy_basic_process.miscellaneous as miscellaneousTools
import tools.data as dataTools
import tools.os as sTools

from amy_basic_process.login import systemLogin

userPrefix = []


class Run:
    def __init__(self) -> None:
        # BASIC PROCESS IMPORTS
        self.vM = importlib.import_module('amy_basic_process.voice_module')
        self.dM = importlib.import_module('amy_basic_process.data_module')
        self.sys = importlib.import_module('amy_basic_process.sys')
        self.task = importlib.import_module('amy_basic_process.task_module')

    def main(self):
        global userPrefix
        input_ = self.vM.ListenInBack.Listener()
        sysA = self.sys.mainProcess
        sysB = self.sys.backgroundProcess
        talk = self.vM.talkProcess
        db = self.dM.AmyData
        osTask = self.task.osModule
        ToolKit = miscellaneousTools.ToolKit
        dTools = dataTools.toolKit
        osTools = sTools.toolKit

        data = dTools.strClearer(input_)

        print(data)

        if data != '' and "amy" in data:
            eAns, task, index, key = db.taskIndexer(data)
            chat = db.chatIndexer(data)

            # Chat
            if data != chat:
                talk.talk(chat + userPrefix[randint(0, len(userPrefix)-1)])
            # Task
            elif key == True:
                talk.talk(eAns)
                eval(task)
            else:
                pass

    def firstRun(self):
        global userPrefix
        global userLvl
        userPrefix = self.dM.login.userPrefix()
        configVoice = self.vM.talkProcess
        configVoice.engVoiceConfig()
        configEnv = self.sys.backgroundProcess
        configEnv.moduleReloader("amy_basic_process.data_module")

    def dataAutoUpdater(self):
        self.dM.AmyData.jsonTaskUpdater()


if __name__ == '__main__':
    worker = ThreadPoolExecutor(max_workers=4)
    backWorker = ThreadPoolExecutor(max_workers=8)
    if systemLogin.verify():
        run = Run()
        run.firstRun()
        while True:
            worker.submit(run.main())
            backWorker.submit(run.dataAutoUpdater())
    else:
        quit()
