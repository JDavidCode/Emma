import mysql.connector
import os
import random
import json

# ImportedPythonLibraries
import emma.config.globals as EMMA_GLOBALS
import os


class Login:
    @staticmethod
    def user_login(email, password):
        # Get an instance of DbHandler
        db_handler = EMMA_GLOBALS.services_db_dt

        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        result = db_handler.execute_query(sql, (email, password))

        if result:
            user_id, user_lvl, user_name, age, genre, user_lang, user_data = result[0]
            rut = f".temp/face_{user_name}.zip"
            EMMA_GLOBALS.tools_da.unbinary(user_data, rut)
            EMMA_GLOBALS.tools_cs.unzipper(
                [(f".temp/face_{user_name}.zip", ".temp/")])

            user_data = (user_id, user_lvl, user_name, age, genre)
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

    @staticmethod
    def user_register(name, email, password, age, genre, lang, data):
        # get an instance of DbHandler
        db_handler = EMMA_GLOBALS.iservices_db

        # Check if email already exists
        sql = "SELECT * FROM users WHERE email=%s"
        row = db_handler.execute_query(sql, (email,))
        if row:
            print("The email already exists")
            return False

        # Insert new user
        sql = "INSERT INTO users (lvl, name, email, password, age, genre, lang, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = EMMA_GLOBALS.tools_cs.to_binary(data)
        values = ("0", name, email, password, age, genre, lang, data)
        db_handler.execute_query(sql, values)
        print("Registering user, please wait...")
        db_handler.commit()
        return True

    @staticmethod
    def invited():
        return True

    @staticmethod
    def user_prefix():
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
