import mysql.connector as SConection
import EmiVoiceProcess.voiceModule as vM

baseConect = SConection.connect(host="localhost", user="root", passwd="", database="emidata")
Bpoint = baseConect.cursor(buffered=True)

def BDInput(Command):
    index = Command
    Bpoint.execute("SELECT * FROM emicommands WHERE Input LIKE" + "'%" + index + "%';")
    print(Bpoint.fetchone)  
    return()

def DBOutput(say):
    say = vM.talkP()