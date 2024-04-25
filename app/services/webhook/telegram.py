import logging
import os
import threading
import traceback
from flask import Flask, request, render_template, jsonify
import requests


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
        self.API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
        self.WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET')
        self.WEBHOOK_HOST = "34.171.193.92"
        self.WEBHOOK_PORT = 8443
        self.WEBHOOK_LISTEN = '0.0.0.0'
        self.webhook_lock = threading.Lock()
        # self.WEBHOOK_SSL_CERT = './webhook_cert.pem'
        # self.WEBHOOK_SSL_PRIV = './webhook_pkey.pem'
        # Quick'n'dirty SSL certificate generation:
        #
        # openssl genrsa -out webhook_pkey.pem 2048
        # openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
        #
        # When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
        # with the same value in you put in self.WEBHOOK_HOST

        self.WEBHOOK_URL_BASE = "%s:%s" % (
            self.WEBHOOK_HOST, self.WEBHOOK_PORT)
        self.WEBHOOK_URL_PATH = "/%s/%s/" % (self.API_TOKEN,
                                             self.WEBHOOK_SECRET)

    def register_routes(self):
        try:
            @self.app.route('/')
            def index():
                return jsonify('TELEGRAM WEBHOOK IS RUNNING')

            @self.app.route(self.WEBHOOK_URL_BASE, methods=['POST'])
            def webhook_handler():
                try:
                    if request.headers.get('content-type') == 'application/json':
                        update = request.get_data().decode('utf-8')
                        self.queue_handler.add_to_queue(
                            'CONSOLE', (self.name, update))
                        self.queue_handler.add_to_queue(
                            'TELEGRAM_WEBHOOK', update)
                        return jsonify({'status': 'ok'}), 200
                except Exception as e:
                    self.handle_error(e)
                    return 'ERROR', 500
        except Exception as e:
            self.handle_error(e)

    def register_telegram_webhook(self):
        '''Registra el webhook en Telegram.'''
        if not self.webhook_lock.acquire(blocking=False):
            # Another pod is already registering the webhook, skip registration
            self.queue_handler.add_to_queue(
                'CONSOLE', (self.name, 'Webhook registration skipped (already registered)'))
            return

        try:
            url = f'https://api.telegram.org/bot{self.API_TOKEN}/setWebhook'
            payload = {'url': self.WEBHOOK_URL_PATH}
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                self.queue_handler.add_to_queue(
                    'CONSOLE', (self.name, 'Webhook registrado con éxito'))
            else:
                self.queue_handler.add_to_queue(
                    'CONSOLE', (self.name, f"Error al registrar el webhook: {response.text}"))
        except Exception as e:
            self.handle_error(e)
        finally:
            self.webhook_lock.release()  # Release the lock even in case of exceptions

    def main(self):
        self.event.wait()
        self.queue_handler.add_to_queue(
            'CONSOLE', [self.name, 'Is Started'])
        try:
            self.register_routes()
            self.register_telegram_webhook()
            self.app.run(host=self.WEBHOOK_LISTEN, port=self.WEBHOOK_PORT, ssl_context=(self.WEBHOOK_SSL_CERT, self.WEBHOOK_SSL_PRIV),
                         debug=True)
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


if __name__ == '__main__':
    pass
