# BasePythonLibraries
import os
# ImportedPythonLibraries
import pywhatkit as PWK
import wikipedia as WK
from tools.data import toolKit as tools

#################################################################################

wLanguaje = WK.set_lang('en')


class webModule:
    def __init__(self):
        pass

    def YTPlayer(index):
        PWK.playonyt(index)
        return 0

    def WhatIS(index):
        wiki = WK.summary(index, 1)
        return wiki


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
