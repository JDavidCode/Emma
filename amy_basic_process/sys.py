import importlib
import sys
import os
from dotenv import unset_key as env
from tools.data import toolKit as tools


class mainProcess:
    def __init__(self) -> None:
        pass


class backgroundProcess:
    def __init__(self) -> None:
        pass

    def amyGuardian():
        pass

    def serverShutdown():
        backgroundProcess.tempClearer()

        clear = ['USERNAME', 'USERLVL', 'USERLANG']
        for i in clear:
            env(".venv/.env", "{}".format(i))
        quit()

    def tempClearer():
        path = '.temp'
        for file in os.listdir(path):
            x = path+'\\'+file
            try:
                os.rmdir(x)
            except:
                pass
            try:
                os.remove(x)
            except:
                pass

    def moduleReloader(index):
        json_type = 'dict'
        diccionary = tools.jsonLoader(
            "res\\json\\module_directory.json", json_type)
        diccionary = diccionary['moduleDirectory']
        key = diccionary.keys()
        try:
            for i in key:
                if index in i:
                    index = diccionary.get(i)
                    print(index)
                    importlib.reload(sys.modules[index])
                    print("module", i, "has been reloaded")
                    importlib.invalidate_caches(sys.modules[index])
        except:
            pass

    def machineCaller(index):
        pass


if __name__ == '__main__':
    mainProcess.tempClearer()
