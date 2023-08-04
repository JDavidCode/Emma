import threading
import emma.globals as EMMA_GLOBALS
import traceback

class InputRouter:
    def __init__(self, console_handler, queue_handler, event_handler):
        self.tag = "IO ROUTER"
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.console_handler = console_handler

        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.console_handler.write(self.tag, "Handling shutdown...")
            self.event_handler.subscribers_shutdown_flag(self)#put it when ready for shutdown
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))


    def main(self):
        self.event.wait()
        while not self.stop_flag:
            # Here suppose that have many io queues than only 1
            try:
                ids, data = self.queue_handler.get_queue("API_INPUT", 0.1, (None, None))
                if ids is None:
                    continue
                self.queue_handler.add_to_queue(
                    'GPT_INPUT', (ids, data))  # Updated to pass a tuple
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))

    def process_responses(self):
        while  not self.stop_flag:
            key, data, session_id = self.queue_handler.get_queue("RESPONSE")
            if key == 's0offline':
                self.command_indexer(keyword=data, off_key=True)

            elif key == 'funcall':
                result = self.command_indexer(keyword=data[0])
                if result is not False:
                    result.append(data[1])
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
            self.console_handler,
        )

        if off_key:
            first_key = next(iter(diccionary))
            args = keyword.replace(first_key, '')
        self.queue_handler.add_to_queue("LOGGING", (self.tag, diccionary))

        if diccionary != None:
            return [diccionary]
        else:
            return False

    def run(self):
        self.event.set()
        response_thread = threading.Thread(target=self.process_responses)
        response_thread.start()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    pass
