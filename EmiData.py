from difflib import SequenceMatcher as SM
import mysql.connector
import EmiVoiceProcess.voiceModule as vM
import brain

baseConect = mysql.connector.connect(host="localhost", user="root", passwd="", database="emi")
Bpoint = baseConect.cursor()

def commands():
    index = vM.voice()
    Bpoint.execute("SELECT * FROM emicommands WHERE input LIKE" + "'%" + index + "%';")
    for fila in Bpoint:
        cID = fila[0]
        vIn = fila[1]
        eAns = fila[2]
        eFunc = fila[3]
    similitud = SM(None,vIn,index).ratio()
    if similitud > 0.7:
        if eAns != '' and eFunc != '':
            vM.talkP(eAns)
            eval(eFunc) #Llamar a una funcion si existe.
            commands()
        elif eAns != '':
            vM.talkP(eAns)
            commands()
    if index != 'ErrorNRI':
        print(index)
    commands()
    


        