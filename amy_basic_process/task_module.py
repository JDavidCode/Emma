# BasePythonLibraries
import os
# ImportedPythonLibraries
import pywhatkit as PWK
import wikipedia as WK

wLanguaje = WK.set_lang('en')

appDiccionary = {'Discord': r"C:\Users\J David\AppData\Local\Discord\Update.exe",
                 'Spotify': r"",
                 'WhatsApp': r"C:\Users\J David\AppData\Local\WhatsApp\Update.exe",
                 'studio': r"D:\Apps\FL Studio\FL.exe"
                 }


def YTPlayer(index):
    PWK.playonyt(index)
    return 0


def WhatIS(index):
    wiki = WK.summary(index, 1)
    return wiki


def OpenApp(index):
    keys = appDiccionary.keys()
    if index in keys:
        get = appDiccionary.get(index)
        os.startfile(get)
    return


if __name__ == '__main__':
    pass
