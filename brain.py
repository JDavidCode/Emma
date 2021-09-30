import pywhatkit as PWK
import wikipedia as WK
import EmiVoiceProcess.voiceModule as vM

input = vM.voice()
wLanguaje = WK.set_lang('es')

def YTPlayer(index):
    if 'Busca' in input:
        index = input.replace('Busca', '')
    if 'Reproduce' in input:
        index = input.replace('Reproduce', '')
    PWK.playonyt(index)
    return(0)

def WhatIS(index):
    if 'Dejame leer' in input:
        index = input.replace('dejame leer', '')
        PWK.search(index)
    if 'lee' in input:
        index = input.replace('lee', '')
        wiki = WK.summary(index, 1)
        vM.talkP(wiki)
    return(0)
