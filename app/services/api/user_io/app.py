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
            user_id = data.get("uid", None)
            whitelist_data = Config.tools.data.yaml_loader(
                "./app/config/withelist.yml")

            if "users_id" in whitelist_data and user_id in whitelist_data["users_id"]:
                socket_id = request.sid
                public_ip = data.get("ip", None)
                session_name = data.get("session_name", "Default Session")
                session_id = data.get("ssid", None)
                device_name = data.get("device_name", "Unknown Device")
                device_id = data.get("did", None)

                session_info = {
                    "session_name": session_name,
                    "session_id": session_id,
                }

                # Verificar y cargar o crear usuario y sesiones
                Config.app.system.admin.agents.session.verify_user(user_id)
                if Config.app.system.admin.agents.session.verify_session(user_id, session_id):
                # Obtener el contenido de la sesión y emitir "load session"
                    chat_content = Config.app.system.admin.agents.session.get_chat(
                        user_id, session_id)
                    self.socketio.emit(
                        "load session", {"session_id": session_id, "chat_content": chat_content})
                     # Check if the session exists in the dictionary
                    if session_id not in self.sessions:
                        self.sessions[session_id] = [socket_id]  # Create a new session entry with a list of socket connections
                    else:
                        self.sessions[session_id].append(socket_id)
                else:
                    self.socketio.emit("connect_error", {
                                       "error": "Session not found or invalid"})
            else:
                self.socketio.emit("connect_error", {"error": "Unauthorized user"})


        @self.socketio.on("message")
        def handle_message(data):
            params = request.args
            user_id = params.get("uid", None)
            ssid = params.get("ssid", None)
            device_id = params.get("did", None)
            sid = request.sid

            whitelist_data = Config.tools.data.yaml_loader(
                "./app/config/withelist.yml")

            if 'users_id' in whitelist_data and user_id in whitelist_data['users_id']:
                # Process the client message here (e.g., broadcast it to other clients)
                data = data.lower()  # Convert data to lowercase
                self.queue_handler.add_to_queue(
                    "API_INPUT", ((sid, ssid, user_id, device_id), data))

                # Broadcast the message to other clients in the same session
                if ssid in self.sessions:
                    if len(self.sessions.get(ssid)) > 1:
                        for socket_id in self.sessions[ssid]:
                            if socket_id != sid:
                                self.socketio.emit("update chat", data, room=socket_id)
            else:
                # Log unauthorized access and send a response to the unauthorized user
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, ("Unauthorized User on socket: ", sid)))
                self.socketio.emit("response", "Unauthorized user", room=sid)


    def process_responses(self):
        while not self.stop_flag:
            ids, data = self.queue_handler.get_queue(
                "API_RESPONSE", 0.1, (None, None))
            if ids is None:
                continue

            ssid = ids[1]
            did = ids[0]
            try:
                print(self.sessions)
                # Send the response to all sockets associated with the session ID
                if ssid in self.sessions:
                    for socket_id in self.sessions[ssid]:
                        self.socketio.emit("response", data, room=socket_id)
            except Exception as e:
                traceback_str = traceback.format_exc()
                self.queue_handler.add_to_queue(
                    "CONSOLE", (self.name, f"ERROR while trying to respond to {ids} request. {e}"))
                self.queue_handler.add_to_queue(
                    "LOGGING", (self.name, (e, traceback_str)))

  
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
