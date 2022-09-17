# BasePythonLibraries
import mysql.connector
from tools.data import toolKit as dTools
import os
import random
import json
from dotenv import load_dotenv
load_dotenv('.venv/.env')
# ImportedPythonLibraries

#################################################################################

# root 2k3/XekPx3E6dqaN

conn = mysql.connector.connect(
    host=os.getenv("HOST"),
    database=os.getenv("DATABASE"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
)

cursor = conn.cursor()
if conn.is_connected():
    print('Database has been connected')
    info_server = conn.get_server_info()
    print(info_server)


class login:
    def userLogin(user, password):
        indexer = (user, )
        userData = ()
        eAns = []
        sql = "SELECT * FROM users WHERE name=%s"
        cursor.execute(sql, indexer)
        rut = '.temp\\face_{}.zip'.format(
            user)
        for fila in cursor:
            userID = fila[0]
            userClass = fila[1]
            userName = fila[2]
            pw = fila[3]
            age = fila[4]
            genre = fila[5]
            face = dTools.fromBinaryToFile(
                fila[6], rut)
            dTools.unzipper(
                '.temp\\face_{}.zip'.format(user), '.temp')
            if user == userName and pw == password:
                userData = userID, userClass, userName, age, genre
                return True, userData
            else:
                return False, userData

    def userRegister(user, pw, age, genre, faceRut):
        indexer = (user, )
        sql = "SELECT * FROM users WHERE name=%s"
        cursor.execute(sql, indexer)
        for fila in cursor:
            username = fila[1]
            if username is not None:
                if user in username:
                    print('The user already exist')
                    return False

        sql2 = "INSERT INTO users (name, password, age, genre, face) VALUES(%s, %s, %s, %s, %s)"
        face = dTools.toBinary(faceRut)
        values = (user, pw, age, genre, face)
        cursor.execute(sql2, values)
        print('Registring U, please wait...')
        conn.commit()
        return True


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
        taskIndexer = dTools.jsonLoader(
            'resources\\json\\task_Directory.json', json_type)
        eAns = []
        eFunc = []
        task = ''
        charts = ''
        key = False

        for i in taskIndexer:
            if i in index:
                task = i
                data = data.replace(i, '')
                charts = len(data)
                data = data[1: charts]
                key = True

        sql = "SELECT * FROM taskdata WHERE input LIKE('{}')".format(task)
        cursor.execute(sql)
        for fila in cursor:
            eAns = fila[2]
            eFunc = fila[3]

        return eAns, eFunc, data, key

    def dataWriter():
        tableI = input('Insert table\'s name: ')
        tableList = ('chatdata', 'funfacts', 'taskdata')
        if tableI not in tableList:
            return print('could not find table in database')
        val1 = input('Set input value\'s: ')
        val2 = input('Set output value\'s: ')
        if tableI == 'chatdata':
            sql = "INSERT INTO chatdata (input, answer) VALUES(%s, %s)"
            val = (val1, val2)
        elif tableI == 'funfacts':
            sql = "INSERT INTO funfacts (input, answer) VALUES(%s, %s)"
            val = (val1, val2)
        elif tableI == 'taskdata':
            sql = "INSERT INTO chatdata (input, answer) VALUES(%s, %s)"
            val3 = input('Set task name: ')
            val = (val1, val2, val3)
        print('Uploading data, please wait...')
        cursor.execute(sql, val)
        conn.commit()
        print('Data has been uploaded')

    def dataUpdater():
        tableI = input('Insert table\'s name: ')
        tableList = ('chatdata', 'funfacts', 'taskdata')
        if tableI not in tableList:
            return print('could not find table in database')
        val1 = input('Set input value\'s: ')
        val2 = input('Set output value\'s: ')
        val4 = input('Insert the data id to update: ')
        if tableI == 'chatdata':
            sql = "UPDATE chatdata SET input=%s, answer=%s WHERE id=%s"
            val = (val1, val2, val4)
        elif tableI == 'funfacts':
            sql = "UPDATE funfacts SET input=%s, answer=%s WHERE id=%s"
            val = (val1, val2, val4)
        elif tableI == 'taskdata':
            sql = "UPDATE taskdata SET input=%s, answer=%s, task=%s WHERE id=%s"
            val3 = input('Set task name: ')
            val = (val1, val2, val3, val4)

        print('Updating data, please wait...')
        cursor.execute(sql, val)
        conn.commit()
        print('Data has been updated')

    def dataRemover():
        tableI = input('Insert table\'s name: ')
        tableList = ('chatdata', 'funfacts', 'taskdata')
        if tableI not in tableList:
            return print('could not find table in database')
        val = [input('Insert the data id to remove: ')]
        if tableI == 'chatdata':
            sql = "DELETE FROM chatdata WHERE id=%s"
        elif tableI == 'funfacts':
            sql = "DELETE FROM funfacts WHERE id=%s"
        elif tableI == 'taskdata':
            sql = sql = "DELETE FROM taskdata WHERE id=%s"
        print('Deleting data, please wait...')
        cursor.execute(sql, val)
        conn.commit()
        print('Data has been removed')


#################################################################################
#################################################################################
#################################################################################


if __name__ == '__main__':
    pass
