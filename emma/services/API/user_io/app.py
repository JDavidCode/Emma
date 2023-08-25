
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import json
import logging
import threading
import traceback
from emma.config.config import Config


class APP:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.app = Flask(__name__)
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.socketio = SocketIO(self.app)
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
                "./emma/config/withelist.yml")

            # Verify if user_id is in the whitelist_data
            if 'users_id' in whitelist_data and user_id in whitelist_data['users_id']:
                # Verify if user_id.json data is in the local storage
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
                    "PROTO_SESSIONS", ('run', {user_id: data, 'socket': socket_id}))

                # Emit the data to the client
                self.socketio.emit("connect", {"session_id": session_id})
            else:
                # User is not in the whitelist, handle it accordingly (e.g., reject the connection)
                self.socketio.emit("connect_error", {
                                   "error": "Unauthorized user"})

        @self.socketio.on("message")
        def handle_message(data):
            params = request.args
            user_id = params.get("user", None)
            session_id = params.get("session", None)
            socket_id = request.sid

            whitelist_data = Config.tools.data.yaml_loader(
                "./emma/config/withelist.yml")

            if 'users_id' in whitelist_data and user_id in whitelist_data['users_id']:
                # Verify if user_id.json data is in the local storage
                data.lower()
                # Get the session_id associated with the current request

                # Add the data and session_id to the queue
                self.queue_handler.add_to_queue(
                    "API_INPUT", ((socket_id, session_id, user_id), data))
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, ((socket_id, session_id, user_id), data)))

            else:
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, ("unauthorized User on socket: ", socket_id)))
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

            # Return the user sessions as JSON response
            return jsonify(user_sessions)

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
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
            # Emit the response to the correct session_id
            try:
                self.socketio.emit("response", data, room=session_id)
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue("CONSOLE",
                                                (self.name, f"ERROR while tryin response to {session_id} request. {e}"))
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (e, traceback_str)))

    def attach_components(self, module_name):
        attachable_module = __import__(module_name)

        for component_name in dir(attachable_module):
            component = getattr(attachable_module, component_name)

            if callable(component):
                self.thread_utils.attach_function(
                    self, component_name, component)
            elif isinstance(component, threading.Thread):
                self.thread_utils.attach_thread(
                    self, component_name, component)
            else:
                self.thread_utils.attach_variable(
                    self, component_name, component)

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
