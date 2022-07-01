# BasePythonLibraries
from difflib import SequenceMatcher as sm
# ImportedPythonLibraries
import mysql.connector as sql
# AppLibraries
import amy_basic_process.voice_module as vM
import amy_basic_process.task_module as tK
import amy_basic_process.tools_module as tools

#################################################################################
#################################################################################
#################################################################################

# root 1234
# Emi Password 2k3/XekPx3E6dqaN
try:
    conn = sql.connect(
        host='127.0.0.1',
        user='Emi',
        password='2k3/XekPx3E6dqaN',
        db='emi'
    )
except:
    print('An error has ocurred while trying connect')
cursor = conn.cursor()
if conn.is_connected():
    print('Database has been connected')
    info_server = conn.get_server_info()
    print(info_server)


class AmyData:
    def __init__():
        pass

    def dataWriter():
        tableI = input('Inserte el nombre de la tabla: ')
        tableList = ('chatdata', 'funfacts', 'taskdata')
        if tableI not in tableList:
            return print('No se ha encontrado la tabla en la base de datos')
        val1 = input('Inserte el valor de Entrada: ')
        val2 = input('Inserte el valor de Salida: ')
        if tableI == 'chatdata':
            sql = "INSERT INTO chatdata (input, answer) VALUES(%s, %s)"
            val = (val1, val2)
        elif tableI == 'funfacts':
            sql = "INSERT INTO funfacts (input, answer) VALUES(%s, %s)"
            val = (val1, val2)
        elif tableI == 'taskdata':
            sql = "INSERT INTO chatdata (input, answer) VALUES(%s, %s)"
            val3 = input('Inserte el nombre de funcion: ')
            val = (val1, val2, val3)
        print('Registrando datos, por favor espere...')
        cursor.execute(sql, val)
        conn.commit()
        print('Datos registrados con exito')

    def dataUpdater():
        tableI = input('Inserte el nombre de la tabla: ')
        tableList = ('chatdata', 'funfacts', 'taskdata')
        if tableI not in tableList:
            return print('No se ha encontrado la tabla en la base de datos')
        val1 = input('Inserte el valor de Entrada: ')
        val2 = input('Inserte el valor de Salida: ')
        val4 = input('Inserte el id de la funcion a actualizar: ')
        if tableI == 'chatdata':
            sql = "UPDATE chatdata SET input=%s, answer=%s WHERE id=%s"
            val = (val1, val2, val4)
        elif tableI == 'funfacts':
            sql = "UPDATE funfacts SET input=%s, answer=%s WHERE id=%s"
            val = (val1, val2, val4)
        elif tableI == 'taskdata':
            sql = "UPDATE taskdata SET input=%s, answer=%s, task=%s WHERE id=%s"
            val3 = input('Inserte el nombre de funcion: ')
            val = (val1, val2, val3, val4)

        print('Actualizando datos, por favor espere...')
        cursor.execute(sql, val)
        conn.commit()
        print('Datos actualizados con exito con exito')

    def dataRemover():
        tableI = input('Inserte el nombre de la tabla: ')
        tableList = ('chatdata', 'funfacts', 'taskdata')
        if tableI not in tableList:
            return print('No se ha encontrado la tabla en la base de datos')
        val = [input('Inserte el ID de el dato a eliminar: ')]
        if tableI == 'chatdata':
            sql = "DELETE FROM chatdata WHERE id=%s"
        elif tableI == 'funfacts':
            sql = "DELETE FROM funfacts WHERE id=%s"
        elif tableI == 'taskdata':
            sql = sql = "DELETE FROM taskdata WHERE id=%s"
        print('Eliminando datos, por favor espere...')
        cursor.execute(sql, val)
        conn.commit()
        print('Datos Eliminados con exito con exito')

    def dataReader(index):
        data = index
        data = tools.DataTool.strClearer(index)
        data2, indexer = tools.DataTool.taskIndexer(data)
        print(indexer)
        # toda cadena que llegue a la base de datos debe llegar sin simbolos
        sql = "SELECT * FROM chatdata WHERE input LIKE('{}')".format(data)
        cursor.execute(sql)
        for fila in cursor:
            cID = fila[0]
            vIn = fila[1]
            eAns = fila[2]
            similitud = sm(None, vIn, data).ratio()
            # WARNING ENGINE VOICE ONLY WORK IN OFFLINE MODE
            if similitud > 0.65 and eAns != None:
                vM.talkProcess.talk(eAns)

        sql2 = "SELECT * FROM taskdata WHERE input LIKE('{}')".format(data2)
        cursor.execute(sql2)
        for fila in cursor:
            cID = fila[0]
            vIn = fila[1]
            eAns = fila[2]
            eFunc = fila[3]
            similitud = sm(None, vIn, data2).ratio()
            # FUNCION DE RESPALDO PARA LLAMAR A LA FUNCION
            print(similitud)
            indexer = indexer
            if similitud > 0.70:
                vM.talkProcess.talk(eAns)
                eval(eFunc)

#################################################################################
#################################################################################
#################################################################################


if __name__ == '__main__':
    pass
