import os
import threading
import requests
import logging
import traceback
from flask import Flask, request, jsonify


class WebHook:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.app = Flask(self.name)
        self.event = threading.Event()
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.webhook_secret = os.getenv("WHATSAPP_WEBHOOK_SECRET")
        self.webhook_path = f"/webhook/{self.webhook_secret}"

    def register_routes(self):
        @self.app.route("/")
        def index():
            return jsonify('WHATSAPP WEBHOOK IS RUNNING')

        
        @self.app.route(self.webhook_path, methods=['POST'])
        def webhook_handler():
                try:
                    update = request.json
                    if 'message' in update:
                        self.queue_handler.add_to_queue(
                            'WHATSAPP_WEBHOOK', update)

                    return jsonify({'status': 'ok'}), 200
                except Exception as e:
                    self.handle_error(e)
                    return 'ERROR', 500

    def main(self):
        self.event.wait()
        self.queue_handler.add_to_queue(
            'CONSOLE', [self.name, 'Is Started'])
        try:
            self.register_routes()
            self.app.run(host='0.0.0.0', port=8000)
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
        error_message = f'Error in {self.name}: {error}'
        if message:
            error_message += f' - {message}'
        traceback_str = traceback.format_exc()
        self.queue_handler.add_to_queue('LOGGING', (self.name, traceback_str))

    def _handle_shutdown(self):
        try:
            self.queue_handler.add_to_queue(
                'CONSOLE', (self.name, 'Handling shutdown...'))
            self.event_handler.subscribers_shutdown_flag(
                self)
        except Exception as e:
            self.handle_error(e)


if __name__ == "__main__":
   pass
