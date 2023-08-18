import threading
import emma.globals as EMMA_GLOBALS
import traceback


class InputRouter:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler

        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)

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
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
        self.event.wait()

        while not self.stop_flag:
            # Here suppose that have many io queues than only 1
            try:
                ids, data = self.queue_handler.get_queue(
                    "API_INPUT", 0.1, (None, None))
                if ids is None:
                    continue
                self.queue_handler.add_to_queue(
                    'GPT_INPUT', (ids, data))  # Updated to pass a tuple
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (e, traceback_str)))

    def process_responses(self):
        while not self.stop_flag:
            key, data, session_id = self.queue_handler.get_queue("RESPONSE")
            if key == 's0offline':
                self.command_indexer(keyword=data, off_key=True)

            elif key == 'funcall':
                result = self.command_indexer(keyword=data[0])
                if result is not False:
                    result.append(data[1])
                    print(type(result), result)
                    self.queue_handler.add_to_queue(
                        'COMMAND', (session_id, result))
            elif key == 'answer':
                self.queue_handler.add_to_queue(
                    'API_RESPONSE', (session_id, data))

    def command_indexer(self, keyword, off_key=False):
        diccionary = EMMA_GLOBALS.tools_da.json_loader(
            EMMA_GLOBALS.stcpath_command_dir,
            keyword,
            "command",

        )

        if off_key:
            first_key = next(iter(diccionary))
            args = keyword.replace(first_key, '')
        self.queue_handler.add_to_queue("LOGGING", (self.name, diccionary))

        if diccionary != None:
            return [diccionary]
        else:
            return False

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
        response_thread = threading.Thread(
            target=self.process_responses, name=f"{self.name}_responses")
        response_thread.start()
        self.queue_handler.add_to_queue("CONSOLE", [self.name, "Is Started"])

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    pass
