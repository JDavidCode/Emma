import threading
import emma.globals as EMMA_GLOBALS
from emma.system.sys_v import SysV
import traceback

class CommandsRouter:
    def __init__(self, console_handler, queue_handler, thread_handler, event_handler):
        self.tag = "COMMAND ROUTER"
        self.bp = SysV(queue_handler, console_handler)
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler

        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.console_handler = console_handler
        self.thread_handler = thread_handler

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.console_handler.write(self.tag, "Handling shutdown...")
            self.event_handler.subscribers_shutdown_flag(self)#put it when ready for shutdown
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))

    def main(self):
        module = ""
        self.event.wait()
        while not self.stop_flag:
            session_id, data = self.queue_handler.get_queue("COMMAND", 0.1, (None, None))
            if session_id is None:
                continue
            dic, args = data
            try:
                module = getattr(EMMA_GLOBALS, dic.get("module"))
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
                self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))

    def execute_command(self, module, function_name, session_id, args=None):
        try:
            # get the function reference
            function = getattr(module, function_name)
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, ("Cannot get Function Ref.", traceback_str))))
        # call the function
        try:
            self.console_handler.write(
                self.tag, [f"trying to execute {function_name}", f"args = {args}"])
            if args == None:
                key, r = function()
                if key:
                    self.queue_handler.add_to_queue(
                        'API_RESPONSE', (session_id, r))
                self.console_handler.write(self.tag, r)
            elif isinstance(args, (int, str)):
                key, r = function(args)
                if key:
                    self.queue_handler.add_to_queue(
                        'API_RESPONSE', (session_id, r))
                self.console_handler.write(self.tag, r)
            elif isinstance(args, dict):
                key, r = function(**args)
                if key:
                    self.queue_handler.add_to_queue(
                        'API_RESPONSE', (session_id, r))
                self.console_handler.write(self.tag, r)

            self.console_handler.write(
                self.tag, [f"{function_name} has been execute", f"args = {args}"])

        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, (f"{function_name} with args = {args} failed or is unknown", traceback_str))))

    def args_identifier(self, args):
        return args

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True
