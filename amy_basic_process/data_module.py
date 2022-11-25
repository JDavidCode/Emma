# BasePythonLibraries
import mysql.connector
import os
import random
import json
from textblob import TextBlob
from dotenv import load_dotenv
from dotenv import set_key
from tools.data import toolKit as dTools
from tools.converters import ToolKit as cTools
load_dotenv('.venv/.env')
# ImportedPythonLibraries

#################################################################################

# root 2k3/XekPx3E6dqaN
userLVL = os.getenv("USERLVL")
conn = mysql.connector.connect(
    host=os.getenv("HOST"),
    database=os.getenv("DATABASE"),
    user=os.getenv("MACHINE"),
    password=os.getenv("PASSWORD"),
)

cursor = conn.cursor()
if conn.is_connected():
    info_server = conn.get_server_info()


class login:
    def userLogin(user, password):
        rut = '.temp/face_{}.zip'.format(user)
        indexer = (user, password)
        userData = ()
        eAns = []
        envKeys = (('USERLVL', userLvl), ('USERNAME',
                   userName), ('USERLANG', userLang))
        sql = "SELECT * FROM users WHERE name=%s AND password=%s "
        cursor.execute(sql, indexer)

        if cursor is not None:
            for row in cursor:
                userID = row[0]
                userLvl = row[1]
                userName = row[2]
                pw = row[3]
                age = row[4]
                genre = row[5]
                userLang = row[6]
                face = cTools.fromBinaryToFile(row[7], rut)
                cTools.unzipper('.temp/face_{}.zip'.format(user), '.temp/')
                if user == userName and pw == password:
                    userData = userID, userLvl, userName, age, genre
                    for i in envKeys:
                        set_key(".venv/.env", i[0], i[1])
                    return True, userData
                else:
                    return False, userData
        else:
            return False, ()

    def userRegister(user, pw, age, genre, faceRut):
        indexer = (user, )
        sql = "SELECT * FROM users WHERE name=%s"
        cursor.execute(sql, indexer)
        for row in cursor:
            username = row[1]
            if username is not None:
                if user in username:
                    print('The user already exist')
                    return False

        sql2 = "INSERT INTO users (name, password, age, genre, face) VALUES(%s, %s, %s, %s, %s, %s)"
        face = cTools.toBinary(faceRut)
        values = ("1", user, pw, age, genre, face)
        cursor.execute(sql2, values)
        print('Registring U, please wait...')
        conn.commit()
        return True

    def invited():
        set_key(".venv/.env", "USERLVL", "1")
        set_key(".venv/.env", "USERNAME", "")
        set_key(".venv/.env", "USERLANG", "en")
        return True

    def userPrefix():
        global userLVL
        pre = ["", "guest", os.getenv("USERNAME"), "sir.", "master",  "boss"]
        invited = (pre[0], pre[1])
        loged = (pre[0], pre[2])
        silver = (pre[2], pre[3])
        pro = (pre[2], pre[3], pre[4])
        admin = (pre[3], pre[4], pre[5])

        if userLVL == "1":
            return invited
        elif userLVL == "2":
            return loged
        elif userLVL == "3":
            return silver
        elif userLVL == "4":
            return pro
        elif userLVL == "5":
            return admin


class AmyData:
    def __init__():
        pass

    def jsonTaskUpdater():
        directory = 'res\\json\\task_Directory.json'
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
        lang = os.getenv("USERLANG")
        if lang != "en":
            index_ = TextBlob(index)
            index_.translate(to='en')
            indexer = (index_, )
        else:
            indexer = (index, )
        eAns = []
        sql = "SELECT * FROM chatdata WHERE input=%s"
        cursor.execute(sql, indexer)
        for row in cursor:
            iClass = row[2]
            if iClass != None:
                indexer = (iClass, )
                sql = "SELECT * FROM chatdata WHERE class=%s"
                cursor.execute(sql, indexer)
                for row in cursor:
                    eAns.append(row[4])
                eAns = dTools.listItemRemover(index, eAns)
                x = len(eAns)-1
                ran = random.randint(0, x)
                eAns = eAns[ran]
                return eAns
            else:
                return index
        return index

    def taskIndexer(index):
        global userLVL
        data = index
        json_type = 'list'
        taskIndexer = dTools.jsonLoader(
            'res\\json\\task_Directory.json', json_type)
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
        for row in cursor:
            if row[1] <= int(userLVL):
                key = True
            else:
                key = False
            eAns = row[3]
            eFunc = row[4]

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
