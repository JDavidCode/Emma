import logging
import threading
import traceback
from flask import Flask, request, jsonify, render_template


class WebHook:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.app = Flask(__name__)
        self.event = threading.Event()
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def register_routes(self):
        try:
            @self.app.route("/")
            def index():
                return render_template("404")

            @self.app.route("/webhook", methods=['POST'])
            def webhook_handler():
                try:
                    update = request.json
                    # Procesar la actualización recibida
                    # Aquí puedes manejar la actualización según tus necesidades
                    # Por ejemplo, responder al mensaje
                    chat_id = update['message']['chat']['id']
                    message_text = update['message']['text']
                    # Aquí puedes realizar acciones basadas en el mensaje recibido
                    return 'OK'
                except Exception as e:
                    self.handle_error(e)
        except Exception as e:
            self.handle_error(e)

    def main(self):
        try:

            self.event.wait()
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])

            self.register_routes()
            self.app.run(host="0.0.0.19", port=88)

            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "API IS RUNNING"))
        except Exception as e:
            self.handle_error(e)

    def run(self):
        self.event.set()

    def _handle_system_ready(self):
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
