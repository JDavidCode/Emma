import json
import threading


class WhitelistAgent:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.whitelist = {}

    def handle_request(self, request, data):
        # Este método maneja una solicitud de la cola
        # Debes implementar la lógica adecuada aquí
        pass

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
            if request is not None and data is not None:
                # Crear un hilo temporal para manejar la solicitud
                request_thread = threading.Thread(
                    target=self.handle_request, args=(request, data))
                request_thread.start()

    def add_user(self, username, additional_info=None):
        if not username or username in self.whitelist:
            print("Invalid username or username already exists.")
            return

        self.whitelist[username] = additional_info
        print(f"User '{username}' added to the whitelist.")
        self.save_whitelist()

    def remove_user(self, username):
        if username in self.whitelist:
            del self.whitelist[username]
            print(f"User '{username}' removed from the whitelist.")
            self.save_whitelist()
        else:
            print(f"User '{username}' is not in the whitelist.")

    def check_user(self, username):
        if username in self.whitelist:
            print(f"User '{username}' is allowed.")
            if self.whitelist[username] is not None:
                print(f"Additional information: {self.whitelist[username]}")
        else:
            print(f"User '{username}' is not in the whitelist.")

    def list_users(self):
        print("Users in the whitelist:")
        for username, info in self.whitelist.items():
            if info is not None:
                print(f"- {username}: {info}")
            else:
                print(f"- {username}")

    def save_whitelist(self):
        try:
            with open('whitelist.json', 'w') as file:
                json.dump(self.whitelist, file)
        except Exception as e:
            print(f"Error saving whitelist: {str(e)}")

    def load_whitelist(self):
        try:
            with open('whitelist.json', 'r') as file:
                self.whitelist = json.load(file)
        except FileNotFoundError:
            # Initialize with an empty whitelist if the file doesn't exist.
            self.whitelist = {}
        except Exception as e:
            print(f"Error loading whitelist: {str(e)}")

    def handle_shutdown(self):  # This for event handling
        self.stop_flag = False

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


# Example usage:
if __name__ == "__main__":
    pass
