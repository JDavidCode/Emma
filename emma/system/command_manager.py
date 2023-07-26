import threading
import emma.globals as EMMA_GLOBALS
from emma.system.sys_v import SysV


class CommandsManager:
    def __init__(self, console_handler, queue_handler, thread_handler):
        self.tag = "Commands Thread"
        self.bp = SysV(queue_handler, console_handler)
        self.queue_handler = queue_handler
        self.stop_flag = False
        self.event = threading.Event()
        self.console_handler = console_handler
        self.thread_handler = thread_handler

    def main(self):
        module = ""
        self.event.wait()
        while not self.stop_flag:
            session_id, data = self.queue_handler.get_queue("COMMAND")

            dic, args = data
            try:
                module = getattr(EMMA_GLOBALS, dic.get("module"))
                # Execute the command
                if dic.get('args_key') == 'args':
                    self.execute_command(module, dic.get(
                        'key'), dic.get('arguments'))
                elif dic.get('args_key') == '*args':
                    self.execute_command(module, dic.get('key'), args)
                else:
                    self.execute_command(module, dic.get('key'))
            except Exception as e:
                self.console_handler.write(self.tag, e)

    def execute_command(self, module, function_name, args=None):
        try:
            # get the function reference
            function = getattr(module, function_name)
        except Exception as e:
            self.console_handler.write(
                self.tag, f"{e}, Cannot get Function Ref.")
        # call the function
        try:
            self.console_handler.write(
                self.tag, [f"trying to execute {function_name}", f"args = {args}"])
            if args == None:
                r = function()
                if r != None:
                    self.console_handler.write(self.tag, r)
            elif isinstance(args, (int, str)):
                r = function(args)
                if r is not None:
                    self.console_handler.write(self.tag, r)
            elif isinstance(args, dict):
                r = function(**args)
                if r is not None:
                    self.console_handler.write(self.tag, r)

            self.console_handler.write(
                self.tag, [f"{function_name} has been execute", f"args = {args}"])

        except Exception as e:
            self.console_handler.write(
                self.tag, f"{function_name} with args = {args} failed or is unknown: {e}"
            )

    def args_identifier(self, args):
        return args

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True
