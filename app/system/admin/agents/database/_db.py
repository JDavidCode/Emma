import threading
import mysql.connector


class DatabaseAgent:
    """
    A class for managing instances of the Database class.
    """

    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.databases = {}

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
        self.event.wait()
        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])

        while not self.stop_flag:
            request, data = self.queue_handler.get_queue(
                self.queue_name, 0.1, (None, None))

    def create_database(self, tag):
        """
        Create a new Database instance.

        Args:
            tag (str): A tag to identify the database manager instance.
            console_handler: An object responsible for handling console output.

        Returns:
            Database: A new Database instance.
        """
        if tag not in self.databases:
            db = Database(tag, self.queue_handler)
            self.databases[tag] = db
            return db
        else:
            raise ValueError(f"Database with tag '{tag}' already exists.")

    def get_database(self, tag):
        """
        Get a Database instance by tag.

        Args:
            tag (str): The tag of the Database instance to retrieve.

        Returns:
            Database: The Database instance associated with the given tag.
        """
        if tag in self.databases:
            return self.databases[tag]
        else:
            raise ValueError(f"Database with tag '{tag}' does not exist.")

    def close_all_connections(self):
        """
        Close all database connections managed by this manager.
        """
        for db in self.databases.values():
            db.close_connection()
            del db

    def handle_shutdown(self):  # This for event handling
        self.stop_flag = False

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


class Database:
    """
    A class for managing a MySQL database connection.
    """

    def __init__(self, tag, queue_handler):
        self.queue_handler = queue_handler
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
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.tag, f"Error connecting to MySQL: {e}"))
            return False

    # Add other database-related methods here...

    def close_connection(self):
        """
        Close the MySQL database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
