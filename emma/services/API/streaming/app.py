import os
import emma.globals as EMMA_GLOBALS
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
import logging
import threading
import traceback


class APP:
    def __init__(self, queue_handler, event_handler):
        self.app = Flask(__name__)
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.tag = "API STREAMING Thread"
        self.socketio = SocketIO(self.app)
        self.stop_flag = False

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.sessions = {}

    def get_final_video_url(self, short_url):
        try:
            response = requests.get(short_url, allow_redirects=True)
            final_url = response.url
            return final_url
        except requests.exceptions.RequestException:
            return None

    def is_valid_video_url(self, url):
        try:
            # Send a HEAD request to get headers without downloading the whole video
            response = requests.head(url)
            content_type = response.headers.get('Content-Type', '')

            # List of allowed video content types
            allowed_video_content_types = [
                'video/mp4', 'video/webm', 'video/ogg']  # Add more as needed

            if content_type in allowed_video_content_types:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False

    def register_routes(self):
        self.event.wait()

        @self.app.route('/')
        def index():
            return render_template('index.html')

        # Evento para unirse a una sala según el SID del cliente
        @self.socketio.on('join')
        def join(sid):
            join_room(sid)

        # Evento para enviar los datos del video al cliente
        @self.socketio.on('request_video')
        def request_video(data):
            video_url = self.get_final_video_url(data)
            sid = request.sid
            if not self.is_valid_video_url(video_url):
                self.socketio.emit('video_not_found', {
                    'message': "the link provided is not an mp4 file"}, room=sid)
                return

            try:
                response = requests.get(video_url, stream=True)

                # Verificar el tipo MIME del contenido
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('video/'):
                    self.socketio.emit('video_not_found', {
                        'message': "the link provided does not contain a video"}, room=sid)
                    return

                for chunk in response.iter_content(chunk_size=2048):
                    if not chunk:
                        continue  # Skip empty chunks
                    self.socketio.emit(
                        'video_chunk', {'chunk': chunk}, room=sid)
            except Exception as e:
                self.socketio.emit('video_not_found', {
                                   'message': str(e)}, room=sid)

        @self.socketio.on("message")
        def handle_message(data):
            params = request.args
            user_id = params.get("user", None)
            session_id = params.get("session", None)
            socket_id = request.sid

            whitelist_data = EMMA_GLOBALS.tools_da.yaml_loader(
                "./emma/config/withelist.yml")

            if 'users_id' in whitelist_data and user_id in whitelist_data['users_id']:
                # Verify if user_id.json data is in the local storage
                data.lower()
                # Your logic for handling authorized users

            else:
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.tag, ("unauthorized User on socket: ", socket_id)))
                self.socketio.emit(
                    "response", "Unauthorized user", room=socket_id)

    def main(self):
        self.queue_handler.add_to_queue("CONSOLE", [self.tag, "Has been instanciate"])
        self.event.wait()
        if not self.stop_flag:
            self.queue_handler.add_to_queue("CONSOLE", [self.tag, "Is Started"])
        self.register_routes()

        try:
            self.socketio.run(self.app, host="0.0.0.0", port=4010)
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.tag, "API IS RUNNING"))
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.tag, (e, traceback_str)))

    def process_responses(self):
        while not self.stop_flag:
            session_id, data = self.queue_handler.get_queue(
                "API_RESPONSE", 0.1, (None, None))
            if session_id is None:
                continue
            # Emit the response to the correct session_id
            try:
                self.socketio.emit("response", data, room=session_id)
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue("CONSOLE",
                                                (self.tag, f"ERROR while trying response to {session_id} request. {e}"))
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.tag, (e, traceback_str)))

    def run(self):
        self.event.set()


    def stop(self):
        self.stop_flag = True

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.tag, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)  # put it when ready for shutdown
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.tag, (e, traceback_str)))


if __name__ == "__main__":
    pass
