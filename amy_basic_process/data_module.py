# BasePythonLibraries
import mysql.connector
import os
import random
import json
from dotenv import load_dotenv
from dotenv import set_key
from tools.data.local.kit import toolKit as localDataTools
from tools.converters.local.kit import toolKit as localConvertersTools
# ImportedPythonLibraries
load_dotenv('.venv/.env')

#################################################################################

# root 2k3/XekPx3E6dqaN
userLVL = ''
conn = mysql.connector.connect(
    host=os.getenv("HOST"),
    database=os.getenv("DATABASE"),
    user=os.getenv("DBUSER"),
    password=os.getenv("PASSWORD"),
)

cursor = conn.cursor()
if conn.is_connected():
    info_server = conn.get_server_info()
    print("Server version ", info_server)


class Login:
    def user_login(email, password):
        indexer = (email, password)
        userData = ()
        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        cursor.execute(sql, indexer)
        result = cursor.fetchone()
        if result is not None:
            userID = result[0]
            userLvl = result[1]
            userName = result[2]
            age = result[5]
            genre = result[6]
            userLang = result[7]
            rut = '.temp/face_{}.zip'.format(userName)
            localConvertersTools.unbinary(result[8], rut)
            localConvertersTools.unzipper(
                [(".temp\\face_{}.zip".format(userName), ".temp\\")])
            userData = userID, userLvl, userName, age, genre
            logged = os.getenv('LOGGED')
            if logged == 'False':
                envKeys = (('USERLVL', userLvl), ('USERNAME',
                                                  userName), ('USERLANG', userLang), ('LOGGED', str(True)))
                for i in envKeys:
                    set_key(".venv/.env", i[0], i[1])
            return True, userData
        else:
            return False, ()

    def user_register(name, email, pw, age, genre, lang, data):
        # check if email already exists
        sql = "SELECT * FROM users WHERE email=%s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        if row is not None:
            print('The email already exists')
            return False

        # insert new user
        sql = "INSERT INTO users (lvl, name, email, password, age, genre, lang, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = localConvertersTools.to_binary(data)
        values = ("0", name, email, pw, age, genre, lang, data)
        cursor.execute(sql, values)
        print('Registering user, please wait...')
        conn.commit()
        return True

    def invited():
        set_key(".venv/.env", "USERLVL", '1')
        set_key(".venv/.env", "USERNAME", input('insert your name: '))
        set_key(".venv/.env", "USERLANG",
                input('select your language en/es: '))
        return True

    def user_prefix():
        global userLVL
        userLVL = os.getenv("USERLVL")
        pre = ["", os.getenv("USERNAME"), "sir.", "master",  "boss"]
        invited = (pre[0], pre[1])
        loged = (pre[0], pre[1])
        silver = (pre[0], pre[1])
        pro = (pre[1], pre[2])
        admin = (pre[2], pre[3], pre[4])

        if userLVL == "0":
            return invited
        elif userLVL == "1":
            return loged
        elif userLVL == "2":
            return silver
        elif userLVL == "3":
            return pro
        elif userLVL == "4":
            return admin
        else:
            return invited


class AmyData:
    def __init__():
        pass

    def json_task_updater():
        directory = 'assets\\json\\command_directory.json'
        sql = "SELECT caller,function_name, module, args_key, arguments, required_lvl FROM functions"
        cursor.execute(sql)
        # parsing sql
        functions = {}
        for function_id, function_name, module, args_key, function_arguments, required_lvl in cursor:
            if args_key == "args":
                functions[function_id] = {"function_name": function_name,
                                          "module": module,
                                          "args_key": args_key,
                                          "arguments": function_arguments,
                                          "required_lvl": required_lvl}
            else:
                functions[function_id] = {"function_name": function_name,
                                          "module": module,
                                          "args_key": args_key,
                                          "required_lvl": required_lvl}

        # Convert the dictionary to a JSON object
        json_data = json.dumps(functions, indent=4)
        # write to file
        with open(directory, 'w') as f:
            f.write(json_data)

    def chat_indexer(index):
        indexer = (index, )
        eAns = []
        sql = "SELECT * FROM chatdata WHERE input=%s"
        cursor.execute(sql, indexer)
        for row in cursor:
            iClass = row[1]
            if iClass != None:
                indexer = (iClass, )
                sql = "SELECT * FROM chatdata WHERE class=%s"
                cursor.execute(sql, indexer)
                for row in cursor:
                    eAns.append(row[3])
                eAns = localDataTools.item_list_remover(index, eAns)
                x = len(eAns)-1
                ran = random.randint(0, x)
                eAns = eAns[ran]
                return eAns
            else:
                return index
        return index

    def data_writer():
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

    def data_updater():
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

    def data_remover():
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
