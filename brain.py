import os
import pywhatkit as PWK
import wikipedia as WK
import EmiBasicProcess.voiceModule as vM

wLanguaje = WK.set_lang('es')

appdic = {'Discord'  : r"C:\Users\J David\AppData\Local\Discord\Update.exe",
          'Spotify'  : r"",
          'WhatsApp' : r"C:\Users\J David\AppData\Local\WhatsApp\Update.exe"
}

def YTPlayer():
    input = vM.voice()
    index = input
    if 'Busca' in input:
        index.replace('Busca', '')
    if 'Reproduce' in input:  
        index.replace('Reproduce', '')
    PWK.playonyt(index)
    return 0

def WhatIS():
    input = vM.voice()
    index = input
    if 'Leo' in input:
        index = index.replace('Leo sobre', '')
        PWK.search(index)                       
    if 'Lee' in input:                               
        index = index.replace('Lee sobre', '')      
        wiki = WK.summary(index, 1)
        vM.talkP(wiki)
    return 0

def OpenApp(index):
    diccionary = appdic
    asd = 'WhatsApp'
    index = index.replace('Abre', '')
    for key in diccionary:
        if index in diccionary.keys(): #if parametrodefuncion in diccionary
            os.startfile(diccionary[index]) 
            break
        else:
            print('No esta la app')
            break
    return 0