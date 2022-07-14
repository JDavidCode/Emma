# BasePythonLibraries
import os
# ImportedPythonLibraries
from tools.data import toolKit as tools

#################################################################################


class webModule:
    def __init__(self):
        pass


class osModule:
    def __init__(self):
        pass

    def OpenApp(index):
        json_type = 'dict'
        diccionary = tools.jsonLoader(
            "resources\\json\\osApp_directory.json", json_type)
        diccionary = diccionary['appDirectory']
        keys = diccionary.keys()
        if index in keys:
            get = diccionary.get(index)
            os.startfile(get)


class mathModule:
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
