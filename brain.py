import pywhatkit as WK
import EmiVoiceProcess.voiceModule as vM

def YTPlayer(index):
    input = vM.voiceProcess()
    if 'Busca' in input:
        index = input.replace('Busca', '')
        print(index)
    if 'Reproduce' in input:
        index = input.replace('Reproduce', '')
        print(index)
    WK.playonyt(index)
