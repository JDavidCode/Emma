# BasePythonLibraries
import os
# ImportedPythonLibraries
import pywhatkit as PWK
import wikipedia as wk
from tools.data import toolKit as tools

#################################################################################


class webModule:
    def __init__(self):
        pass

    def YTPlayer(index):
        PWK.playonyt(index)
        return 0

    def WhatIS(index):
        wLanguaje = wk.set_lang('en')
        result = ''
        try:
            search = wk.search(index)
            result = wk.summary(search, 10)
            print(result)
        except:
            print("some error has ocurred while trying colect data")
            pass
        return result


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
