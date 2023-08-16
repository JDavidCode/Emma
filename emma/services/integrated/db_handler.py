# BasePythonLibraries
import mysql.connector
import os
import random
import json

# ImportedPythonLibraries
import emma.globals as EMMA_GLOBALS

#################################################################################


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


class DBHandler:
    def __init__(self, queue_handler):
        self.tag = 'I-SERIVCES DB'
        self.queue_handler = queue_handler
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                port="3307",
                database="emma",
                user="root",
                password="root",
            )

            self.cursor = self.conn.cursor()
            if self.conn.is_connected():
                info_server = self.conn.get_server_info()
                print("Server version ", info_server)
                os.environ["SQL_CONNECTION"] = "True"
            else:
                print("Cannot connect to the server")
                os.environ["SQL_CONNECTION"] = "False"
        except Exception as e:
            print(
                f"An error occurred while trying to connect to the database: {e}\n The server continues running but some functions can be stopped."
            )
            os.environ["SQL_CONNECTION"] = "False"

    def json_task_updater(self):
        if os.environ.get("SQL_CONNECTION") != "True":
            return
        directory = "emma_functions.json"  # Change this to your desired file path
        sql = "SELECT id, caller, function_name, module, args_key, arguments, required_lvl FROM functions"
        self.cursor.execute(sql)

        functions = {}
        for (
            function_id,
            caller,
            function_name,
            module,
            args_key,
            function_arguments,
            required_lvl,
        ) in self.cursor:
            function_data = {
                "caller": caller,
                "function_name": function_name,
                "module": module,
                "args_key": args_key,
                "arguments": function_arguments,
                "required_lvl": required_lvl,
            }
            functions[function_id] = function_data

        # Write functions dictionary to a JSON file
        with open(directory, "w") as f:
            json.dump(functions, f, indent=4)
        print("Functions data has been updated in the JSON file.")

    def data_writer(self):
        if os.environ.get("SQL_CONNECTION") != "True":
            return

        # Fetch the list of available table names from the database
        self.cursor.execute("SHOW TABLES")
        tables = [table[0] for table in self.cursor]

        if not tables:
            print("No tables found in the database.")
            return

        print("Available tables:", ", ".join(tables))

        table_i = input("Insert table's name: ")
        if table_i not in tables:
            return print("Could not find the specified table in the database")

        columns = []
        self.cursor.execute(f"SHOW COLUMNS FROM {table_i}")
        for column in self.cursor:
            columns.append(column[0])

        input_values = {}
        for column in columns:
            value = input(f"Set value for '{column}': ")
            input_values[column] = value

        placeholders = ", ".join(["%s"] * len(input_values))
        columns_str = ", ".join(input_values.keys())
        values = tuple(input_values.values())

        sql = f"INSERT INTO {table_i} ({columns_str}) VALUES ({placeholders})"

        print("Uploading data, please wait...")
        self.cursor.execute(sql, values)
        self.conn.commit()
        print("Data has been uploaded")

    def data_updater(self):
        if os.environ.get("SQL_CONNECTION") != "True":
            return
        table_list = ("chatdata", "funfacts", "taskdata")
        table_i = input(f"Insert table's name ({', '.join(table_list)}): ")
        if table_i not in table_list:
            return print("Could not find table in the database")

        data_id = input("Insert the data id to update: ")
        input_value = input("Set input value: ")
        output_value = input("Set output value: ")

        if table_i == "taskdata":
            task_name = input("Set task name: ")
            sql = "UPDATE taskdata SET input=%s, answer=%s, task=%s WHERE id=%s"
            val = (input_value, output_value, task_name, data_id)
        else:
            sql = f"UPDATE {table_i} SET input=%s, answer=%s WHERE id=%s"
            val = (input_value, output_value, data_id)

        print("Updating data, please wait...")
        self.cursor.execute(sql, val)
        self.conn.commit()
        print("Data has been updated")

    def data_remover(self):
        if os.environ.get("SQL_CONNECTION") != "True":
            return
        table_list = ("chatdata", "funfacts", "taskdata")
        table_i = input(f"Insert table's name ({', '.join(table_list)}): ")
        if table_i not in table_list:
            return print("Could not find table in the database")

        data_id = input("Insert the data id to remove: ")

        if table_i == "taskdata":
            sql = "DELETE FROM taskdata WHERE id=%s"
        else:
            sql = f"DELETE FROM {table_i} WHERE id=%s"

        print("Deleting data, please wait...")
        self.cursor.execute(sql, (data_id,))
        self.conn.commit()
        print("Data has been removed")

    def close_connection(self):
        if os.environ.get("SQL_CONNECTION") != "True":
            return
        self.cursor.close()
        self.conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    pass
