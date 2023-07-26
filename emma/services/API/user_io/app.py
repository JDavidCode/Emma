import base64
import emma.globals as EMMA_GLOBALS
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import json
import logging
import threading


class APP:
    def __init__(self, queue_handler, console_handler):
        self.app = Flask(__name__)
        self.history = self.json_history()
        self.console_handler = console_handler
        self.queue_handler = queue_handler
        self.event = threading.Event()
        self.tag = "API Thread"
        self.socketio = SocketIO(self.app)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.sessions = {}

    def json_history(self):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(module_dir)
        date = EMMA_GLOBALS.task_msc.date_clock(2)
        history_dir = os.path.join(
            parent_dir, "user_io", "history")  # Relative folder path
        history_path = os.path.join(history_dir, f"{date}.json")

        if not os.path.exists(history_dir):
            # Create the directory if it doesn't exist
            os.makedirs(history_dir)
        if not os.path.exists(history_path):
            # Create the file if it doesn't exist
            with open(history_path, "w") as f:
                json.dump({}, f, indent=4)
        return history_path

    def register_routes(self):
        self.event.wait()

        @self.app.route("/")
        def home():
            return render_template("index.html")

        @self.socketio.on("connect")
        def connect():
            data = request.args
            # Get the client's IP addresses
            public_ip = EMMA_GLOBALS.tools_net.get_public_ip(request)
            # Generate a unique session ID (you can use UUID or any other suitable method)
            session_id = EMMA_GLOBALS.tools_gs.generate_emd_id()
            device_name = data.get("device_name")
            session_name = data.get("session_name")
            user_id = data.get("user")
            ip4, ip6 = EMMA_GLOBALS.tools_net.get_client_ip_addresses(request)
            device_id = base64.urlsafe_b64encode(
                ip6.encode("utf-8")).decode("utf-8")

            # Register the session
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

            self.console_handler.write(self.tag, data)
            self.queue_handler.add_to_queue("NET_SESSIONS", {user_id: data})

            # emit the data to the client
            self.socketio.emit("connect", {"session_id": session_id})

        @self.socketio.on("message")
        def handle_message(data):
            data.lower()
            session_id = request.sid  # Get the session_id associated with the current request

            # Add the data and session_id to the queue
            self.queue_handler.add_to_queue(
                "API_INPUT", (session_id, data))
            self.console_handler.write(self.tag, data)

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
        self.event.wait()
        self.register_routes()

        try:
            self.socketio.run(self.app, host="0.0.0.0", port=3018)
            self.console_handler.write(self.tag, "API IS RUNNING")
        except Exception as e:
            self.console_handler.write(self.tag, str(e))

    def process_responses(self):
        while True:
            session_id, data = self.queue_handler.get_queue("API_RESPONSE")
            # Emit the response to the correct session_id
            self.socketio.emit("response", data, room=session_id)

    def run(self):
        self.event.set()
        response_thread = threading.Thread(target=self.process_responses)
        response_thread.start()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    pass
