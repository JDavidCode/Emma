import os
import pywhatkit as PWK
import wikipedia as WK
import amy_basic_process.voice_module as vM

wLanguaje = WK.set_lang('en')

appdic = {'Discord': r"C:\Users\J David\AppData\Local\Discord\Update.exe",
          'Spotify': r"",
          'WhatsApp': r"C:\Users\J David\AppData\Local\WhatsApp\Update.exe",
          'studio': r"D:\Apps\FL Studio\FL.exe"
          }


def YTPlayer(index):
    if 'play on' in index:
        index.replace('play on', '')
    PWK.playonyt(index)
    return 0


def WhatIS(index):
    wiki = WK.summary(index, 1)
    vM.talkProcess.talk(wiki)
    return 0


def OpenApp(index):
    keys = appdic.keys()
    if index in keys:
        get = appdic.get(index)
        print(get)
        os.startfile(get)

    return


if __name__ == '__main__':
    pass
