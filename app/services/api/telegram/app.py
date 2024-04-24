import os
import threading
import traceback
import telebot


class App:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.response_thread = None
        self.bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_API_TOKEN"))
        self.webhook_secret = os.getenv('TELEGRAM_WEBHOOK_SECRET')

    def register_routes(self):
        try:
            @self.bot.message_handler(commands=['start'])
            def send_welcome(message):
                self.bot.reply_to(message, "¡Hola mundo!, Mi nombre es Emma.")

            # @self.bot.message_handler(commands=['help', 'ayuda'])
            # def send_help(message):
            #   self.bot.reply_to(message, "Busca ayuda en otro lado")

            @self.bot.message_handler(func=lambda message: message.text is not None and message.reply_to_message is None)
            def echo_text(message):
                try:
                    cid = message.chat.id
                    uid = message.from_user.id
                    if message.text != "":
                        self.queue_handler.add_to_queue(
                            "TELEGRAM_API_TEXT", ((uid, cid), message.text, "TELEGRAM_API"))
                except Exception as e:
                    self.handle_error(e)

            @self.bot.message_handler(content_types=['audio'])
            def handle_audio(message):
                pass

            @self.bot.message_handler(content_types=['document'])
            def handle_docs(message):
                try:
                    cid = message.chat.id
                    uid = message.from_user.id
                    fid = message.document.file_unique_id
                    doc_name = message.document.file_name
                    file_info = self.bot.get_file(
                        message.document.file_id)

                    file_bytes = self.bot.download_file(
                        file_path=file_info.file_path)
                    file_path = f"app/common/.temp/{message.document.file_name}"
                    with open(file_path, 'wb') as f:
                        f.write(file_bytes)

                    self.queue_handler.add_to_queue(
                        "TELEGRAM_API_DOC", ("write", (uid, cid, fid), (doc_name, file_path), "TELEGRAM_API"))
                except Exception as e:
                    self.handle_error(e)

            @self.bot.message_handler(func=lambda message: message.reply_to_message is not None and message.reply_to_message.document is not None)
            def reply_to_doc(message):
                try:
                    cid = message.chat.id
                    uid = message.from_user.id
                    reply_message = message.reply_to_message
                    fid = reply_message.document.file_unique_id

                    original_text = message.text
                    self.queue_handler.add_to_queue(
                        "TELEGRAM_API_DOC", ("read", (uid, cid, fid), original_text, "TELEGRAM_API"))
                except Exception as e:
                    self.handle_error(e)
        except Exception as e:
            self.handle_error(e)

    def process_responses(self):
        try:
            while not self.stop_flag:
                ids, data = self.queue_handler.get_queue(
                    "TELEGRAM_API_RESPONSE", 0.1, (None, None))
                if ids is None:
                    continue
                else:
                    self.bot.send_message(ids[1], data)
        except Exception as e:
            self.handle_error(e)

    def main(self):
        self.event.wait()
        self.bot.remove_webhook()
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Is Started"])
        try:
            self.register_routes()
            while not self.stop_flag:
                data = self.queue_handler.get_queue(
                    "TELEGRAM_WEBHOOK", 0.1, (None))
                if data is None:
                    continue
                else:
                    update_json = data.get('update')
                    update = telebot.types.Update.de_json(
                        update_json)
                    self.bot.process_new_updates([update])
        except Exception as e:
            self.handle_error(e)

    def run(self):
        self.event.set()

    def _handle_system_ready(self):
        self.response_thread = threading.Thread(
            target=self.process_responses, name=f"{self.name}_RESPONSES")
        self.response_thread.start()
        self.run()
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
    pass
