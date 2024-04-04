import threading
import traceback
import telebot


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

    def register_routes(self):
        self.event.wait()

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.reply_to(message, "Hola mundo, Yo soy Emma.")

        @self.bot.message_handler(commands=['help', 'ayuda'])
        def send_help(message):
            self.bot.reply_to(message, "Busca ayuda en otro lado")

        @self.bot.message_handler(content_types=['document'])
        def handle_docs_audio(message):
            cid = message.chat.id
            uid = message.from_user.id
            self.queue_handler.add_to_queue("CONSOLE", (self.name, message))
            self.queue_handler.add_to_queue("TELEGRAM_API_DOC", ((uid, cid), message.document, "TELEGRAM_API"))

        @self.bot.message_handler(func=lambda m: True)
        def echo_all(message):
            cid = message.chat.id
            uid = message.from_user.id
            self.queue_handler.add_to_queue(
                "TELEGRAM_API_TEXT", ((uid, cid), message.text, "TELEGRAM_API"))

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
            self.bot.polling(none_stop=True)
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
