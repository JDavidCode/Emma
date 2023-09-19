import mysql.connector

class DatabaseManager:
    """
    A class for managing MySQL database connections and operations.

    Args:
        tag (str): A tag to identify the database manager instance.
        console_handler: An object responsible for handling console output.
    """
    def __init__(self, tag, console_handler):
        self.console_handler = console_handler
        self.tag = tag
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.conn = None

    def connect(self, host, user, password, database):
        """
        Connect to a MySQL database.

        Args:
            host (str): The hostname of the database server.
            user (str): The username for authentication.
            password (str): The password for authentication.
            database (str): The name of the database to connect to.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
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
        """
        Create a table in the connected MySQL database.

        Args:
            table_name (str): The name of the table to create.
            columns (str): A string defining the table columns and their data types.

        Returns:
            bool: True if the table creation was successful, False otherwise.
        """
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
        """
        Insert data into a table in the connected MySQL database.

        Args:
            table_name (str): The name of the table to insert data into.
            data (tuple): A tuple containing data values to be inserted.

        Returns:
            bool: True if the data insertion was successful, False otherwise.
        """
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
        """
        Execute a SQL query and fetch the results.

        Args:
            query (str): The SQL query to execute.

        Returns:
            list: A list containing the fetched data, or None if there was an error.
        """
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
        """
        Update data in a table in the connected MySQL database.

        Args:
            table_name (str): The name of the table to update data in.
            set_clause (str): The SET clause of the SQL update statement.
            where_clause (str): The WHERE clause of the SQL update statement.

        Returns:
            bool: True if the data update was successful, False otherwise.
        """
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
        """
        Delete data from a table in the connected MySQL database.

        Args:
            table_name (str): The name of the table to delete data from.
            where_clause (str): The WHERE clause of the SQL delete statement.

        Returns:
            bool: True if the data deletion was successful, False otherwise.
        """
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
        """
        Close the MySQL database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
