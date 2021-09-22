from difflib import SequenceMatcher as SM
import EmiDatabase.EmiDataConnect as bM
import EmiVoiceProcess.voiceModule as vM

#  V   V   O O   I I I   C C  E E E
#   V V   O   O    I    C     E E
#    V     O O   I I I   C C  E E E

vM.micConfig()

def commands():
    bM.Bpoint.execute("SELECT * FROM emicommands")
    for fila in bM.Bpoint:
        cID = fila[0]
        vIn = fila[1]
        eAns = fila[2]
        eFunc = fila[3] 
        similitud = SM(None,vIn,vM.voiceProcess()).ratio()
        print(similitud)
        if similitud > 0.8:
            vM.talkProcess(eAns)
            commands()
        else :
            commands()