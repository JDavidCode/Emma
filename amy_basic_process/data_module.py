# BasePythonLibraries
from multiprocessing.managers import DictProxy
import random
import json
# ImportedPythonLibraries
import mysql.connector as sql
import amy_basic_process.tools_module as tools
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

    def jsonTaskUpdater():
        directory = 'resources\\json\\task_Directory.json'
        diccionary = {"indexer": []}
        dbDiccionary = {"taskIndexer": []}
        sql = "SELECT input FROM taskdata"
        cursor.execute(sql)
        # Getting data from JSON
        with open(directory) as f:
            direct = json.load(f)
            for i in direct["taskIndexer"]:
                for y in i:
                    x = 0
                    diccionary['indexer'].append(i[x])
                    x += 1
            f.close()
        # Getting data from db
        for i in cursor:
            for y in i:
                dbDiccionary['taskIndexer'].append(y)
        # if there is new data in db, json has to be update
        with open(directory, 'w') as f:
            for i in dbDiccionary:
                if i not in diccionary['indexer']:
                    json.dump(dbDiccionary, f, indent=2)
                    break

    def chatIndexer(index):
        indexer = (index, )
        eAns = []
        sql = "SELECT * FROM chatdata WHERE input=%s"
        cursor.execute(sql, indexer)
        for fila in cursor:
            iClass = fila[1]
            if iClass != None:
                indexer = (iClass, )
                sql = "SELECT * FROM chatdata WHERE class=%s"
                cursor.execute(sql, indexer)
                for fila in cursor:
                    eAns.append(fila[3])
                x = len(eAns)-1
                ran = random.randint(0, x)
                eAns = eAns[ran]
                return eAns
            else:
                return index
        return index

    def taskIndexer(index):
        data = index
        json_type = 'list'
        taskIndexer = tools.DataTools.jsonLoader(
            'resources\\json\\task_Directory.json', json_type)
        eAns = []
        eFunc = []
        task = ''
        charts = ''
        loader = False

        for i in taskIndexer:
            if i in index:
                task = i
                data = data.replace(i, '')
                charts = len(data)
                data = data[1: charts]
                loader = True

        sql = "SELECT * FROM taskdata WHERE input LIKE('{}')".format(task)
        cursor.execute(sql)
        for fila in cursor:
            eAns = fila[2]
            eFunc = fila[3]

        return eAns, eFunc, data, loader

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


#################################################################################
#################################################################################
#################################################################################


if __name__ == '__main__':
    pass
