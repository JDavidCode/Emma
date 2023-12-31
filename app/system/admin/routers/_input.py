import threading
import traceback
import logging
from app.config.config import Config


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
            message = (self.name, "Handling shutdown...")
            self.queue_handler.add_to_queue("CONSOLE", message)
            self.event_handler.subscribers_shutdown_flag(self)
        except Exception as e:
            self.handle_error(e)

    def main(self):
        message = (self.name, "Has been instantiated")
        self.queue_handler.add_to_queue("CONSOLE", message)
        self.event.wait()

        while not self.stop_flag:
            try:
                ids, data = self.queue_handler.get_queue(
                    "API_INPUT", timeout=0.1, default=(None, None))
                if ids is not None:
                    self.queue_handler.add_to_queue('GPT_INPUT', (ids, data))
            except Exception as e:
                self.handle_error(e)

    def process_responses(self):
        while not self.stop_flag:
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
        dictionary = Config.tools.data.json_loader(
            Config.paths._command_dir,
            keyword,
            "command",
        )

        if off_key:
            first_key = next(iter(dictionary))
            args = keyword.replace(first_key, '')
        message = (self.name, dictionary)

        if dictionary is not None:
            return [dictionary]
        else:
            return False

    def run(self):
        self.event.set()
        response_thread = threading.Thread(
            target=self.process_responses, name=f"{self.name}_responses")
        response_thread.start()
        message = (self.name, "Is Started")
        self.queue_handler.add_to_queue("CONSOLE", message)

    def stop(self):
        self.stop_flag = True

    def handle_error(self, error):
        logging.error(f"Error in {self.name}: {error}")
        traceback_str = traceback.format_exc()
        logging.error(traceback_str)


if __name__ == "__main__":
    pass  # Add your application logic here
