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

    def main(self):
        self.event.wait()
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Is Started"])

    def web_api_input(self):
        while not self.stop_flag:
            try:
                ids, data, channel = self.queue_handler.get_queue(
                    "WEB_API_TEXT", timeout=0.1, default=(None, None, None))
                if ids is not None:
                    self.queue_handler.add_to_queue(
                        'GPT_INPUT', (ids, data, channel))
            except Exception as e:
                self.handle_error(e)

    def telegram_api_text(self):
        while not self.stop_flag:
            try:
                ids, data, channel = self.queue_handler.get_queue(
                    "TELEGRAM_API_TEXT", timeout=0.1, default=(None, None, None))
                if ids != None:
                    self.queue_handler.add_to_queue(
                        'GPT_INPUT', (ids, data, channel))
            except Exception as e:
                self.handle_error(e)

    def telegram_api_doc(self):
        while not self.stop_flag:
            try:
                _, ids, data, channel = self.queue_handler.get_queue(
                    "TELEGRAM_API_DOC", timeout=0.1, default=(None, None, None, None))
                if ids != None:
                    if _ == 'write':
                        self.queue_handler.add_to_queue(
                            'AIDOC_READER', (ids, data, channel))
                    elif _ == 'read':
                        self.queue_handler.add_to_queue(
                            'AIDOC_READER_QUESTION', (ids, data, channel))
            except Exception as e:
                self.handle_error(e)

    def gpt_responses(self):
        while not self.stop_flag:
            key, data, ids, channel = self.queue_handler.get_queue(
                "GPT_RESPONSE")
            if key == 's0offline':
                self.command_indexer(keyword=data, off_key=True)
            elif key == 'funcall':
                result = self.command_indexer(keyword=data[0])
                if result is not False:
                    result.append(data[0])
                    self.queue_handler.add_to_queue(
                        'COMMAND', (ids, result, channel))
            elif key == 'answer':
                self.queue_handler.add_to_queue(
                    f'{channel}_RESPONSE', (ids, data))

    def aidoc_responses(self):
        while not self.stop_flag:
            key, ids, data,  channel = self.queue_handler.get_queue(
                "AIDOC_READER_RESPONSE")
            if key == "load":
                self.queue_handler.add_to_queue(
                    f'{channel}_RESPONSE', (ids, f"Document {data} has been loaded"))
            elif key == "response":
                self.queue_handler.add_to_queue(
                    f'{channel}_RESPONSE', (ids, data))

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

    def _handle_system_ready(self):
        web_api_thread = threading.Thread(
            target=self.web_api_input, name=f"{self.name}_WEB")
        web_api_thread.start()
        telegram_api_text_thread = threading.Thread(
            target=self.telegram_api_text, name=f"{self.name}_TELEGRAM_TEXT")
        telegram_api_text_thread.start()
        telegram_api_doc_thread = threading.Thread(
            target=self.telegram_api_doc, name=f"{self.name}_TELEGRAM_DOC")
        telegram_api_doc_thread.start()
        gpt_response_thread = threading.Thread(
            target=self.gpt_responses, name=f"{self.name}_GPT_RESPONSES")
        gpt_response_thread.start()
        aidoc_responses_thread = threading.Thread(
            target=self.aidoc_responses, name=f"{self.name}_AIDOC_RESPONSES")
        aidoc_responses_thread.start()
        return True

    def stop(self):
        self.stop_flag = True

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
    pass  # Add your application logic here
