from sqlalchemy import Column, create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
import traceback


class DatabaseAgent:
    def __init__(self, name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.databases = {}

    def connect(self, host, user, password, database):
        try:
            # Check if the host is already in the database dictionary
            if host not in self.databases:
                # If not, establish a new connection
                engine_url = f'mysql+pymysql://{user}:{password}@{host}/{database}'
                engine = create_engine(engine_url)
                self.databases[host] = {}
                self.databases[host]['engine'] = engine
                self.databases[host]['metadata'] = MetaData()
                self.databases[host]['metadata'].bind = engine
            else:
                # If the host exists, check if the database is already connected
                if database in self.databases[host]:
                    # If yes, return the existing connection
                    return self.databases[host]['engine']
                else:
                    # If not, establish a new connection for the database
                    engine_url = f'mysql+pymysql://{user}:{password}@{host}/{database}'
                    engine = create_engine(engine_url)
                    self.databases[host]['engine'] = engine
                    self.databases[host]['metadata'] = MetaData()
                    self.databases[host]['metadata'].bind = engine

            return self.databases[host]['engine']
        except SQLAlchemyError as e:
            self.handle_error(e)
            return None

    def close_connection(self, host, database):
        try:
            # Check if the host and database exist in the dictionary
            if host in self.databases and database in self.databases[host]:
                # Close the connection
                self.databases[host]['engine'].dispose()
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
        try:
            engine_url = f'mysql+pymysql://{user}:{password}@{host}'
            engine = create_engine(engine_url)
            with engine.connect() as connection:
                connection.execute(
                    "CREATE DATABASE IF NOT EXISTS {}".format(new_database))
            return True
        except SQLAlchemyError as e:
            self.handle_error(e)
            return False

    def create_table_from_dict(self, table_name, fields):
        try:
            metadata = MetaData()
            metadata.bind = self.get_connection()
            table = Table(table_name, metadata)
            for field, data_type in fields.items():
                table.append_column(Column(field, data_type))
            metadata.create_all()
            return True
        except SQLAlchemyError as e:
            self.handle_error(e)
            return False

    def get_connection(self):
        for host in self.databases:
            for database_conn in self.databases[host].values():
                return database_conn
        return None

    def close_all_connections(self):
        try:
            for host in self.databases:
                self.databases[host]['engine'].dispose()
            self.databases.clear()
            return True
        except Exception as e:
            self.handle_error(e)
            return False

    def _handle_system_ready(self):
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
