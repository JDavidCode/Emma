import threading
import traceback
import telebot
import mimetypes


class App:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.TOKEN = "7043619976:AAHa1x9nm2ooqdyxIRoS2V6ud7Np81C82PI"
        self.bot = telebot.TeleBot(self.TOKEN)

        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.response_thread = None
        self.sessions = {}
        self.user_context = {}

    def register_routes(self):
        self.event.wait()

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.reply_to(message, "¡Hola mundo!, Mi nombre es Emma.")

        # @self.bot.message_handler(commands=['help', 'ayuda'])
        # def send_help(message):
        #   self.bot.reply_to(message, "Busca ayuda en otro lado")

        @self.bot.message_handler(func=lambda message: message.text is not None and message.reply_to_message is None)
        def echo_text(message):
            cid = message.chat.id
            uid = message.from_user.id
            if message.text != "":

                self.queue_handler.add_to_queue(
                    "TELEGRAM_API_TEXT", ((uid, cid), message.text, "TELEGRAM_API"))

        @self.bot.message_handler(content_types=['audio'])
        def handle_audio(message):
            pass

        @self.bot.message_handler(content_types=['document'])
        def handle_docs(message):
            cid = message.chat.id
            uid = message.from_user.id
            fid = message.document.file_unique_id
            doc_name = message.document.file_name
            file_info = self.bot.get_file(
                message.document.file_id)

            file_bytes = self.bot.download_file(file_path=file_info.file_path)
            file_path = f"app/common/.temp/{message.document.file_name}"
            with open(file_path, 'wb') as f:
                f.write(file_bytes)

            # self.queue_handler.add_to_queue("CONSOLE", (self.name, file_bytes))
            self.queue_handler.add_to_queue(
                "TELEGRAM_API_DOC", ("write", (uid, cid, fid), (doc_name, file_path), "TELEGRAM_API"))

        @self.bot.message_handler(func=lambda message: message.reply_to_message is not None and message.reply_to_message.document is not None)
        def reply_to_doc(message):
            cid = message.chat.id
            uid = message.from_user.id
            reply_message = message.reply_to_message
            fid = reply_message.document.file_unique_id

            _ask = reply_message.document

            # Aquí puedes acceder a los datos del mensaje original y del documento adjunto
            original_text = message.text
            self.queue_handler.add_to_queue(
                "TELEGRAM_API_DOC", ("read", (uid, cid, fid), original_text, "TELEGRAM_API"))

    def process_responses(self):
        while not self.stop_flag:
            ids, data = self.queue_handler.get_queue(
                "TELEGRAM_API_RESPONSE", 0.1, (None, None))
            if ids is None:
                continue
            else:
                self.bot.send_message(ids[1], data)

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instantiated"])
        self.event.wait()
        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])

        try:
            self.register_routes()
            self.bot.infinity_polling()
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "API IS RUNNING"))
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))

    def run(self):
        self.event.set()
        self.response_thread = threading.Thread(
            target=self.process_responses, name=f"{self.name}_RESPONSES")
        self.response_thread.start()

    def stop(self):
        self.stop_flag = True

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


if __name__ == "__main__":
    pass
