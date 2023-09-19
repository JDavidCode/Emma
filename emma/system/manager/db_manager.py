import mysql.connector

class DatabaseManager:
    def __init__(self, tag, console_handler):
        self.console_handler = console_handler
        self.tag = tag
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.conn = None

    def connect(self, host, user, password, database):
        self.tag = f"{self.tag}-{user}"
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except mysql.connector.Error as e:
            self.console_handler.write(self.tag, f"Error connecting to MySQL: {e}")
            return False

    def create_table(self, table_name, columns):
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
                self.conn.commit()
                return True
            else:
                self.console_handler.write(self.tag, "MySQL connection not established.")
                return False
        except mysql.connector.Error as e:
            self.console_handler.write(self.tag, f"Error creating table: {e}")
            return False

    def insert_data(self, table_name, data):
        try:
            if self.conn:
                cursor = self.conn.cursor()
                query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s']*len(data))})"
                cursor.execute(query, data)
                self.conn.commit()
                return True
            else:
                self.console_handler.write(self.tag, "MySQL connection not established.")
                return False
        except mysql.connector.Error as e:
            self.console_handler.write(self.tag, f"Error inserting data: {e}")
            return False

    def query_data(self, query):
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
            else:
                self.console_handler.write(self.tag, "MySQL connection not established.")
                return None
        except mysql.connector.Error as e:
            self.console_handler.write(self.tag, f"Error querying data: {e}")
            return None

    def update_data(self, table_name, set_clause, where_clause):
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}")
                self.conn.commit()
                return True
            else:
                self.console_handler.write(self.tag, "MySQL connection not established.")
                return False
        except mysql.connector.Error as e:
            self.console_handler.write(self.tag, f"Error updating data: {e}")
            return False

    def delete_data(self, table_name, where_clause):
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute(f"DELETE FROM {table_name} WHERE {where_clause}")
                self.conn.commit()
                return True
            else:
                self.console_handler.write(self.tag, "MySQL connection not established.")
                return False
        except mysql.connector.Error as e:
            self.console_handler.write(self.tag, f"Error deleting data: {e}")
            return False

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
