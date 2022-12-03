import importlib
import sys
import os
from dotenv import set_key
from tools.data.local.kit import toolKit as localDataTools


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
        backgroundProcess.envClearer()
        quit()

    def envClearer():
        clear = [('USERNAME', ''), ('USERLVL', '1'), ('USERLANG', '')]
        for i in clear:
            set_key(".venv/.env", i[0], i[1])

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
        diccionary = localDataTools.jsonLoader(
            "assets\\json\\module_directory.json", json_type)
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

    def globalVariableSetter():
        pass


if __name__ == '__main__':
    mainProcess.tempClearer()
