#BasePythonLibraries
from difflib import SequenceMatcher as sm 
import re
#ImportedPythonLibraries
########################################
#AppLibraries
import mysql.connector as sql
import voice_module as vM

#################################################################################
#################################################################################
#################################################################################

#root 1234
#Emi Password 2k3/XekPx3E6dqaN
try:
    conn = sql.connect(
        host= '127.0.0.1',
        user= 'Emi',
        password= '2k3/XekPx3E6dqaN',
        db= 'emi'
    )
except:
    print('An error has ocurred while trying connect')

cursor = conn.cursor()

if conn.is_connected():
        print('Database has been connected')
        info_server=conn.get_server_info()
        print(info_server)


#################################################################################
#################################################################################
#################################################################################


def chat(index):
    #toda cadena que llegue a la base de datos debe llegar sin simbolos
    if '\'' in index:
        patron = '[\']'
        regex = re.compile(patron)
        index = regex.sub('', index)
    else:
        pass
    cursor.execute("SELECT * FROM chatdata WHERE input LIKE" + "'%" + index + "%';")
    for fila in cursor:
        cID = fila[0]
        vIn = fila[1]
        eAns = fila[2]
        similitud = sm(None,vIn,index).ratio()
        #WARNING ENGINE VOICE ONLY WORK IN OFFLINE MODE
        if similitud > 0.70:
            vM.talkProcess(eAns)

    cursor.execute("SELECT * FROM taskdata WHERE input LIKE" + "'%" + index + "%';")
    for fila in cursor:
        cID = fila[0]
        vIn = fila[1]
        eAns = fila[2]
        eFunc = fila[3]
        similitud = sm(None,vIn,index).ratio()
        if similitud > 0.70:
            vM.talkProcess(eAns)
            eval(eFunc)

#################################################################################
#################################################################################
#################################################################################


if __name__ == '__main__':
    conn.close()