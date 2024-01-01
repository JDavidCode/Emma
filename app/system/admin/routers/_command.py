import threading
import logging
import traceback
from app.config.config import Config


class CommandRouter:
    def __init__(self, name, queue_name, queue_handler, event_handler, thread_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.thread_handler = thread_handler

        self.event_handler.subscribe(self)

    def handle_shutdown(self):
        try:
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            # Consider implementing shutdown logic here
            self.event_handler.subscribers_shutdown_flag(self)
        except Exception as e:
            self.handle_error(e)

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instantiated"])
        self.event.wait()

        while not self.stop_flag:
            ids, data = self.queue_handler.get_queue(
                "COMMAND", 0.1, (None, None))
            if ids is None or data is None:
                continue

            command_info, args = data
            try:
                module = Config.app.system.admin.agents.sys.get_nested_attribute(
                    Config, command_info.get("module"))
                function_name = command_info.get("key")
                args_key = command_info.get('args_key')

                self.execute_command(module, function_name,
                                     ids, args, args_key)
            except Exception as e:
                self.handle_error(e)

    def execute_command(self, module, function_name, ids, args, args_key):
        try:
            function = getattr(module, function_name)
        except AttributeError as e:
            self.handle_error(e, f"Error executing function {function_name}")
            return

        try:
            if args_key == 'args':
                result = function(*args)
            elif args_key == '*args':
                result = function(args)
            else:
                result = function()

            if result:
                key, r = result
                if key:
                    self.queue_handler.add_to_queue(
                        'API_RESPONSE', (ids, r))
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, f"{function_name} executed with args {args}. Session: {ids}"))
            else:
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, f"Function {function_name} result is None. Session: {ids}"))
                self.queue_handler.add_to_queue(
                    "CONSOLE", (self.name, "Function result is None."))

        except Exception as e:
            self.handle_error(e, f"Error executing function {function_name}")

    def run(self):
        self.event.set()
        self.queue_handler.add_to_queue("CONSOLE", [self.name, "Is Started"])

    def stop(self):
        self.stop_flag = True

    def handle_error(self, error, message=None):
        error_message = f"Error in {self.name}: {error}"
        if message:
            error_message += f" - {message}"
        logging.error(error_message)
        traceback_str = traceback.format_exc()
        logging.error(traceback_str)


if __name__ == "__main__":
    pass  # Add your application logic here
