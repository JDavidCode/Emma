import mysql.connector
import traceback


class DatabaseAgent:
    """
    A class for managing instances of the Database class.
    """

    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.databases = {}

    def connect(self, host, user, password, database):
        """
        Connect to a MySQL database.

        Args:
            host (str): The hostname of the database server.
            user (str): The username for authentication.
            password (str): The password for authentication.
            database (str): The name of the database to connect to.

        Returns:
            mysql.connector.connection.MySQLConnection: A MySQLConnection object if the connection was successful, None otherwise.
        """
        try:
            # Check if the host is already in the database dictionary
            if host not in self.databases:
                # If not, establish a new connection
                conn = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
                )
                # Create a new dictionary entry for the host
                self.databases[host] = {}
            else:
                # If the host exists, check if the database is already connected
                if database in self.databases[host]:
                    # If yes, return the existing connection
                    return self.databases[host][database]
                else:
                    # If not, establish a new connection for the database
                    conn = mysql.connector.connect(
                        host=host,
                        user=user,
                        password=password,
                        database=database
                    )

            # Add the connection to the database dictionary
            self.databases[host][database] = conn
            return conn
        except mysql.connector.Error as e:
            self.handle_error(e)
            return None

    def close_connection(self, host, database):
        """
        Close a connection to a MySQL database.

        Args:
            host (str): The hostname of the database server.
            database (str): The name of the database to close the connection for.

        Returns:
            bool: True if the connection was successfully closed, False otherwise.
        """
        try:
            # Check if the host and database exist in the dictionary
            if host in self.databases and database in self.databases[host]:
                # Close the connection
                self.databases[host][database].close()
                # Remove the connection from the dictionary
                del self.databases[host][database]
                return True
            else:
                # Connection doesn't exist
                print("Connection does not exist.")
                return False
        except Exception as e:
            self.handle_error(e)
            return False

    def create_database(self, host, user, password, new_database):
        """
        Create a new database on a MySQL server.

        Args:
            host (str): The hostname of the MySQL server.
            user (str): The username for authentication.
            password (str): The password for authentication.
            new_database (str): The name of the new database to create.

        Returns:
            bool: True if the database was successfully created, False otherwise.
        """
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            cursor = conn.cursor()
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS {}".format(new_database))
            cursor.close()
            conn.close()
            return True
        except mysql.connector.Error as e:
            self.handle_error(e)
            return False

    def create_table_from_dict(cursor, table_name, fields):
        """
        Create a table in a MySQL database using a dictionary representing the table structure.

        Args:
            cursor (mysql.connector.cursor.MySQLCursor): The MySQL cursor object.
            table_name (str): The name of the table to create.
            fields (dict): A dictionary representing the table structure where keys are field names and values are field data types.

        Returns:
            bool: True if the table was successfully created, False otherwise.
        """
        try:
            # Construct SQL query to create table
            query = "CREATE TABLE IF NOT EXISTS {} (".format(table_name)
            for field, data_type in fields.items():
                query += "{} {}, ".format(field, data_type)
            # Remove the trailing comma and space, then close the parentheses
            query = query[:-2] + ")"

            # Execute SQL query
            cursor.execute(query)
            return True
        except mysql.connector.Error as e:
            print("MySQL Error:", e)
            return False

    def get_connection(self, host, database):
        """
        Retrieve a connection object from the self.databases dictionary.

        Args:
            host (str): The hostname of the database server.
            database (str): The name of the database.

        Returns:
            mysql.connector.connection.MySQLConnection or None: The connection object if found, None otherwise.
        """
        if host in self.databases and database in self.databases[host]:
            return self.databases[host][database]
        else:
            return None


    def close_all_connections(self):
        """
        Close all connections stored in the self.databases dictionary.

        Returns:
            bool: True if all connections were successfully closed, False otherwise.
        """
        try:
            # Iterate over each host in the databases dictionary
            for host in self.databases:
                # Iterate over each database connection in the host
                for database_conn in self.databases[host].values():
                    # Close the connection
                    database_conn.close()
            # Clear the databases dictionary
            self.databases.clear()
            return True
        except Exception as e:
            self.handle_error(e)
            return False

    def _handle_system_ready(self):
        self.run()
        return True

    def handle_error(self, error, message=None):
        error_message = f"Error in {self.name}: {error}"
        if message:
            error_message += f" - {message}"
        traceback_str = traceback.format_exc()
        self.queue_handler.add_to_queue("LOGGING", (self.name, traceback_str))

    def _handle_shutdown(self):
        try:
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)
        except Exception as e:
            self.handle_error(e)


if __name__ == "__main__":
    pass
