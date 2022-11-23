# BasePythonLibraries
from concurrent.futures import ThreadPoolExecutor
from random import randint


# Tools Libraries
import tools.miscellaneous as miscellaneousTools
import tools.data as dataTools
import amy_basic_process.sys as sysA
import tools.os as sTools

# Task Libraries
from amy_basic_process.task_module import osModule as osTask
from amy_basic_process.task_module import webModule as webTask

# ETC
import amy_basic_process.voice_module as vM
import amy_basic_process.data_module as dM
from amy_basic_process.login import systemLogin


class Run:
    def __init__(self) -> None:
        pass

    def main():
        prefix = dM.login.userPrefix()
        input_ = vM.ListenInBack.Listener()
        ToolKit = miscellaneousTools.ToolKit
        dTools = dataTools.toolKit
        sys = sysA.mainProcess
        osTools = sTools.toolKit
        talk = vM.talkProcess
        db = dM.AmyData
        data = ToolKit.strClearer(input_)
        print(input_, prefix)

        if data != '':
            eAns, task, index, key = db.taskIndexer(data)
            chat = db.chatIndexer(data)

            # Chat
            if data != chat:
                talk.talk(chat + prefix[randint(0, len(prefix)-1)])
            # Task
            elif key == True:
                talk.talk(eAns)
                eval(task)
            else:
                pass

    def dataAutoUpdater():
        dM.AmyData.jsonTaskUpdater()


if __name__ == '__main__':
    worker = ThreadPoolExecutor(max_workers=4)
    backWorker = ThreadPoolExecutor(max_workers=8)
    vM.talkProcess.engVoiceConfig()
    vM.talkProcess.talk(
        '')
    if systemLogin.verify():
        while True:
            worker.submit(Run.main())
            backWorker.submit(Run.dataAutoUpdater())
    else:
        quit()
