import importlib
import threading
from emma.config.config import Config
import traceback


class CommandRouter:
    def __init__(self, name, queue_name, queue_handler, event_handler, thread_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.thread_handler = thread_handler

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)  # put it when ready for shutdown
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))

    def main(self):
        module = ""
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
        self.event.wait()

        while not self.stop_flag:
            session_id, data = self.queue_handler.get_queue(
                "COMMAND", 0.1, (None, None))
            if session_id is None or data is None:
                continue
            dic, args = data

            try:
                module = Config.system.core.sys_variations.get_nested_attribute(Config, dic.get("module"))
                # Execute the command
                if dic.get('args_key') == 'args':
                    self.execute_command(module, function_name=dic.get(
                        'key'), session_id=session_id, args=dic.get('arguments'))
                elif dic.get('args_key') == '*args':
                    self.execute_command(module, function_name=dic.get(
                        'key'), session_id=session_id, args=args)
                else:
                    self.execute_command(module, function_name=dic.get(
                        'key'), session_id=session_id)

            except Exception as e:
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (e, traceback_str)))

    def execute_command(self, module, function_name, session_id, args=None):
        try:
            # get the function reference
            function = getattr(module, function_name)
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, (e, "Error executing function.", function_name)))
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, ("Cannot get Function Ref.", traceback_str))))

        # call the function
        try:
            self.queue_handler.add_to_queue("LOGGING", (self.name, [
                                            f"trying to execute {function_name} with args = {args}. Session: {session_id} "]))
            if args is None:
                result = function()
            elif isinstance(args, (int, str)):
                result = function(args)
            elif isinstance(args, dict):
                result = function(**args)
            else:
                result = None

            if result is not None:
                key, r = result
                if key:
                    self.queue_handler.add_to_queue(
                        'API_RESPONSE', (session_id, r))
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name,  (f"{function_name} has been executed", f"args = {args}", session_id)))
            else:
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (f"Function {function_name} result is None, unable to unpack the result.", session_id)))
                self.queue_handler.add_to_queue(
                    "CONSOLE", (self.name, "Function result is None, unable to unpack the result."))

        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, f"Error executing {function_name} function.. {e}"))
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, ("Error executing function.", traceback_str))))

    def args_identifier(self, args):
        return args

    def attach_components(self, module_name):
        attachable_module = __import__(module_name)

        for component_name in dir(attachable_module):
            component = getattr(attachable_module, component_name)

            if callable(component):
                self.thread_utils.attach_function(
                    self, component_name, component)
            elif isinstance(component, threading.Thread):
                self.thread_utils.attach_thread(
                    self, component_name, component)
            else:
                self.thread_utils.attach_variable(
                    self, component_name, component)

    def run(self):
        self.event.set()
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Is Started"])

    def stop(self):
        self.stop_flag = True
