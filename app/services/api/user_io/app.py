from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room
from flask_cors import CORS
import logging
import threading
import traceback
from app.config.config import Config


class App:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        CORS(self.app)  # Apply CORS to the Flask app
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.response_thread = None
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.sessions = {}

    def register_routes(self):
        self.event.wait()

        @self.app.route("/")
        def home():
            return render_template("index.html")

        @self.socketio.on("connect")
        def connect():
            data = request.args

            user_id = data.get("user", None)
            whitelist_data = Config.tools.data.yaml_loader(
                "./app/config/withelist.yml")

            if 'users_id' in whitelist_data and user_id in whitelist_data['users_id']:
                socket_id = request.sid
                public_ip = data.get("ip", None)
                session_name = data.get("session_name", "Default Session")
                session_id = data.get("session", None)
                device_name = data.get("device_name", "Unknown Device")
                device_id = data.get("device_id", None)

                session_info = {
                    'session_name': session_name,
                    'session_id': session_id,
                }

                data = {
                    'device_name': device_name,
                    'device_id': device_id,
                    'session': session_info,
                    'public_ips': public_ip
                }
                self.queue_handler.add_to_queue(
                    "SESSION_AGENT", ('run', {user_id: data, 'socket': socket_id}))
                self.socketio.emit("connect", {"session_id": session_id})
            else:
                self.socketio.emit("connect_error", {
                                   "error": "Unauthorized user"})

        @self.socketio.on("message")
        def handle_message(data):
            params = request.args
            user_id = params.get("user", None)
            session_id = params.get("session", None)
            socket_id = request.sid

            whitelist_data = Config.tools.data.yaml_loader(
                "./app/config/withelist.yml")

            if 'users_id' in whitelist_data and user_id in whitelist_data['users_id']:
                vardw = 1
                # Process the client message here (e.g., broadcast it to other clients)
                # self.socketio.emit("message", data, room=session_id)  # Uncomment if broadcasting
            else:
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, ("Unauthorized User on socket: ", socket_id)))
                self.socketio.emit(
                    "response", "Unauthorized user", room=socket_id)

                @self.app.route("/get_user_sessions", methods=["GET"])
                def get_user_sessions():
                    user_id = request.args.get("user_id")
                    self.queue_handler.add_to_queue(
                        "NET_SESSIONS", {"user_id": user_id})
                    user_sessions = [
                        {"session_name": "Session 1", "session_id": "12345"},
                        {"session_name": "Session 2", "session_id": "67890"},
                        # Add more session dictionaries as needed
                    ]
                    return jsonify(user_sessions)

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instantiated"])
        self.event.wait()
        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])
        self.register_routes()

        try:
            self.socketio.run(self.app, host="0.0.0.0",
                              port=3018, allow_unsafe_werkzeug=True)
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "API IS RUNNING"))
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))

    def process_responses(self):
        while not self.stop_flag:
            session_id, data = self.queue_handler.get_queue(
                "API_RESPONSE", 0.1, (None, None))
            if session_id is None:
                continue
            try:
                self.socketio.emit("response", data, room=session_id)
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue("CONSOLE",
                                                (self.name, f"ERROR while trying to respond to {session_id} request. {e}"))
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (e, traceback_str)))

    def run(self):
        self.event.set()
        self.response_thread = threading.Thread(
            target=self.process_responses, name=f"{self.name} process_responses")
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
