# BasePythonLibraries
from concurrent.futures import ThreadPoolExecutor

# Tools Libraries
import tools.miscellaneous as miscellaneousTools
import tools.data as dataTools
import tools.root as rootTools
import tools.os as sTools

# Task Libraries
from amy_basic_process.task_module import osModule as osTask
from amy_basic_process.task_module import webModule as webTask

# Work
from work import trading
# ETC
import amy_basic_process.voice_module as vM
import amy_basic_process.data_module as dM
from amy_basic_process.login import systemLogin


class Cores:
    def __init__(self) -> None:
        pass

    def MainCore():
        input_ = vM.ListenInBack.Listener()
        ToolKit = miscellaneousTools.ToolKit
        dTools = dataTools.toolKit
        rTools = rootTools.toolKit
        osTools = sTools.toolKit
        talk = vM.talkProcess
        db = dM.AmyData
        data = ToolKit.strClearer(input_)

        print(input_)

        if data != '':
            eAns, task, index, key = db.taskIndexer(data)
            chat = db.chatIndexer(data)

            # Chat
            if data != chat:
                talk.talk(chat)
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
        'Welcome to Coffe Now Systems, This is a Beta version of the Amy Assistant')
    if systemLogin.verify():
        while True:
            worker.submit(Cores.MainCore())
            backWorker.submit(Cores.dataAutoUpdater())
    else:
        quit()
