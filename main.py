import EmiVoiceProcess.voiceModule as vM
import EmiDatabase.EmiDataConfig as bM

#  V   V   O O   I I I   C C  E E E
#   V V   O   O    I    C     E E
#    V     O O   I I I   C C  E E E

vM.engVoiceConfig()
vM.micConfig()


bM.Bpoint.execute("SELECT * FROM emicommands")
for fila in bM.Bpoint:
    cID = fila[0]
    vIn = fila[1]
    eAns = fila[2]
    eFunc = fila[3]
    vM.talkProcess(eAns)