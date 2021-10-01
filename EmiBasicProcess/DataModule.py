from difflib import SequenceMatcher as SM
import mysql.connector, os
import EmiBasicProcess.voiceModule as vM
import brain

baseConect = mysql.connector.connect(host="localhost", user="root", passwd="", database="emi")
Bpoint = baseConect.cursor()

def commands():
    index = vM.voice()
    Bpoint.execute("SELECT * FROM efuncx WHERE input LIKE" + "'%" + index + "%';")
    for fila in Bpoint:
        cID = fila[0]
        vIn = fila[1]
        eAns = fila[2]
        eFunc = fila[3]
        similitud = SM(None,vIn,index).ratio()
        if similitud > 0.60:
            if eAns != '' and eFunc != '':
                vM.talkP(eAns)
                eval(eFunc) #Llamar a una funcion si existe.
            elif eAns != '':
                vM.talkP(eAns)
        elif index != 'ErrorNRI':
            print(index)

    recall=commands()
    return recall

    


        