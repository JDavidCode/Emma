# BasePythonLibraries
import mysql.connector
import os
import random
import json

# ImportedPythonLibraries
import emma.config.globals as EMMA_GLOBALS

#################################################################################


class Login:
    def user_login(email, password):
        indexer = (email, password)
        user_data = ()
        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        cursor.execute(sql, indexer)
        result = cursor.fetchone()
        if result is not None:
            user_id = result[0]
            user_lvl = result[1]
            user_name = result[2]
            age = result[5]
            genre = result[6]
            user_lang = result[7]
            rut = f".temp/face_{user_name}.zip"
            EMMA_GLOBALS.tools_da.unbinary(result[8], rut)
            EMMA_GLOBALS.tools_cs.unzipper(
                [(f".temp/face_{user_name}.zip", ".temp/")])
            user_data = user_id, user_lvl, user_name, age, genre
            logged = os.getenv("LOGGED")
            if logged == "False":
                env_keys = (
                    ("user_lvl", user_lvl),
                    ("user_name", user_name),
                    ("user_lang", user_lang),
                    ("LOGGED", str(True)),
                )
                for i in env_keys:
                    os.environ[i[0]] = i[1]
            return True, user_data
        else:
            return False, ()

    def user_register(name, email, password, age, genre, lang, data):
        # check if email already exists
        sql = "SELECT * FROM users WHERE email=%s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        if row is not None:
            print("The email already exists")
            return False

        # insert new user
        sql = "INSERT INTO users (lvl, name, email, password, age, genre, lang, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = EMMA_GLOBALS.tools_cs.to_binary(data)
        values = ("0", name, email, password, age, genre, lang, data)
        cursor.execute(sql, values)
        print("Registering user, please wait...")
        conn.commit()
        return True

    def invited():
        os.environ["user_lvl"] = "1"
        os.environ["user_name"] = input("insert your name: ")
        os.environ["user_lang"] = input("select your language en/es: ")
        return True

    def user_prefix():
        global user_lvl
        user_lvl = os.getenv("user_lvl")
        pre = ["", os.getenv("user_name"), "sir.", "master", "boss"]
        invited = (pre[0], pre[1])
        loged = (pre[0], pre[1])
        silver = (pre[0], pre[1])
        pro = (pre[1], pre[2])
        admin = (pre[2], pre[3], pre[4])

        if user_lvl == "0":
            return invited
        elif user_lvl == "1":
            return loged
        elif user_lvl == "2":
            return silver
        elif user_lvl == "3":
            return pro
        elif user_lvl == "4":
            return admin
        else:
            return invited


class EmmaData:
    def __init__(self):
        self.connect()

    def connect(self):
        global cursor
        global conn
        try:
            conn = mysql.connector.connect(
                host="localhost",
                port="3307",
                database="emma",
                user="root",
                password="root",
            )

            cursor = conn.cursor()
            if conn.is_connected():
                info_server = conn.get_server_info()
                print("Server version ", info_server)
            else:
                print("Cannot Connect To the server ")
        except Exception as e:
            print(
                f"An error ocurred while triying to connect to the database {e} \n the server continue running but some functions can be stops")
            os.environ['SQL_CONNECTION'] = False

    def json_task_updater():
        if not os.environ.get('SQL_CONNECTION'):
            return
        directory = "emma/assets/json/command_directory.json"
        sql = "SELECT caller,function_name, module, args_key, arguments, required_lvl FROM functions"
        cursor.execute(sql)
        # parsing sql
        functions = {}
        for (
            function_id,
            function_name,
            module,
            args_key,
            function_arguments,
            required_lvl,
        ) in cursor:
            if args_key == "args":
                functions[function_id] = {
                    "function_name": function_name,
                    "module": module,
                    "args_key": args_key,
                    "arguments": function_arguments,
                    "required_lvl": required_lvl,
                }
            else:
                functions[function_id] = {
                    "function_name": function_name,
                    "module": module,
                    "args_key": args_key,
                    "required_lvl": required_lvl,
                }

        # Convert the dictionary to a JSON object
        json_data = json.dumps(functions, indent=4)
        # write to file
        with open(directory, "w") as f:
            f.write(json_data)

    def data_writer():
        if not os.environ.get('SQL_CONNECTION'):
            return
        table_i = input("Insert table's name: ")
        table_list = ("chatdata", "funfacts", "taskdata")
        if table_i not in table_list:
            return print("could not find table in database")
        val1 = input("Set input value's: ")
        val2 = input("Set output value's: ")
        if table_i == "chatdata":
            sql = "INSERT INTO chatdata (input, answer) VALUES(%s, %s)"
            val = (val1, val2)
        elif table_i == "funfacts":
            sql = "INSERT INTO funfacts (input, answer) VALUES(%s, %s)"
            val = (val1, val2)
        elif table_i == "taskdata":
            sql = "INSERT INTO chatdata (input, answer) VALUES(%s, %s)"
            val3 = input("Set task name: ")
            val = (val1, val2, val3)
        print("Uploading data, please wait...")
        cursor.execute(sql, val)
        conn.commit()
        print("Data has been uploaded")

    def data_updater():
        if not os.environ.get('SQL_CONNECTION'):
            return
        table_i = input("Insert table's name: ")
        table_list = ("chatdata", "funfacts", "taskdata")
        if table_i not in table_list:
            return print("could not find table in database")
        val1 = input("Set input value's: ")
        val2 = input("Set output value's: ")
        val4 = input("Insert the data id to update: ")
        if table_i == "chatdata":
            sql = "UPDATE chatdata SET input=%s, answer=%s WHERE id=%s"
            val = (val1, val2, val4)
        elif table_i == "funfacts":
            sql = "UPDATE funfacts SET input=%s, answer=%s WHERE id=%s"
            val = (val1, val2, val4)
        elif table_i == "taskdata":
            sql = "UPDATE taskdata SET input=%s, answer=%s, task=%s WHERE id=%s"
            val3 = input("Set task name: ")
            val = (val1, val2, val3, val4)

        print("Updating data, please wait...")
        cursor.execute(sql, val)
        conn.commit()
        print("Data has been updated")

    def data_remover():
        if not os.environ.get('SQL_CONNECTION'):
            return
        table_i = input("Insert table's name: ")
        table_list = ("chatdata", "funfacts", "taskdata")
        if table_i not in table_list:
            return print("could not find table in database")
        val = [input("Insert the data id to remove: ")]
        if table_i == "chatdata":
            sql = "DELETE FROM chatdata WHERE id=%s"
        elif table_i == "funfacts":
            sql = "DELETE FROM funfacts WHERE id=%s"
        elif table_i == "taskdata":
            sql = sql = "DELETE FROM taskdata WHERE id=%s"
        print("Deleting data, please wait...")
        cursor.execute(sql, val)
        conn.commit()
        print("Data has been removed")


#################################################################################
#################################################################################
#################################################################################


if __name__ == "__main__":
    pass
