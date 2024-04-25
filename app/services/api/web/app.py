import threading
import traceback
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import logging
from app.config.config import Config


class App:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.app = Flask(self.name)
        self.socketio = SocketIO(self.app)
        self.stop_flag = False
        self.response_thread = None
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.sessions = {}

    def register_routes(self):
        try:
            @self.app.route("/")
            def index():
                return jsonify('MAIN API IS RUNNING')

            @self.socketio.on("connect")
            def connect():
                try:
                    client_id = request.sid  # Unique client ID
                    self.socketio.emit("start_connection", {
                                       "client_id": client_id})
                    return jsonify({"response": "Connected"})
                except Exception as e:
                    self.handle_error(e)

            @self.app.route("/get_user", methods=["POST"])
            def get_user():
                try:
                    data = request.get_json()
                    uid = data.get('uid')
                    _, content = Config.app.system.admin.agents.user.auth.get_user(
                        uid)
                    if _:
                        return jsonify(content), 200
                    else:
                        return jsonify({"error": content}), 400
                except Exception as e:
                    self.handle_error(e)

            @self.socketio.on("message")
            def handle_message(data):
                try:
                    uid = data.get("uid")
                    device_id = data.get("device_id")
                    chat_id = data.get("chat_id")
                    sid = request.sid

                    if device_id not in self.sessions:
                        self.sessions[uid] = [sid, device_id]
                    else:
                        self.sessions[uid].append([sid, device_id])

                    # Convert data to lowercase
                    data = data.get("message").lower()
                    self.queue_handler.add_to_queue(
                        "WEB_API_TEXT", ((sid, uid, chat_id, device_id), data, "WEB_API"))

                    # Broadcast the message to other clients in the same session
                    if uid in self.sessions:
                        if len(self.sessions.get(uid)) > 1:
                            for socket_id in self.sessions[uid][0]:
                                if socket_id != sid:
                                    self.socketio.emit(
                                        "update_chat", data, room=socket_id)
                except Exception as e:
                    self.handle_error(e)

            @self.app.route("/login", methods=['POST'])
            def user_login():
                try:
                    data = request.json
                    _, response = Config.app.system.admin.agents.user.auth.user_login(
                        data)
                    if _:
                        return jsonify({"uid": response})
                    else:
                        return jsonify({"ERROR": response})
                except Exception as e:
                    self.handle_error(e)
                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)

            @self.app.route("/signup", methods=['POST'])
            def user_signup():
                try:
                    data = request.json
                    _, response = Config.app.system.admin.agents.user.auth.user_signup(
                        data)
                    if _:
                        return jsonify({"uid": response})
                    else:
                        return jsonify({"ERROR": response})

                except Exception as e:
                    self.handle_error(e)
                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)

            @self.app.route("/create_chat", methods=['POST'])
            def create_chat():
                try:
                    uid = request.form.get('uid')
                    gid = request.form.get('gid')
                    chat_name = request.form.get('name')
                    chat_description = request.form.get('description')
                    _, response = Config.app.system.admin.agents.user.auth.create_chat(
                        _id=uid, name=chat_name, description=chat_description)
                    if _:
                        response_data = {'status': 'success',
                                         'message': response[0]}
                        self.socketio.emit("update_chat_list", response[1])
                        return jsonify(response_data)

                except Exception as e:
                    self.handle_error(e)

                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)

            @self.app.route("/edit_chat", methods=['POST'])
            def edit_chat():
                try:
                    uid = request.form.get('uid')
                    gid = request.form.get('gid')
                    cid = request.form.get('cid')
                    # _, response = Config.app.system.admin.agents.user.auth.delete_group(uid, gid)
                    return jsonify({"response": "Edit chat", "uid": uid})

                    if _:
                        response_data = {'status': 'success',
                                         'message': response}
                        return jsonify(response_data)

                except Exception as e:
                    self.handle_error(e)
                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)

            @self.app.route("/delete_chat", methods=['POST'])
            def delete_chat():
                try:

                    uid = request.form.get('uid')
                    gid = request.form.get('gid')
                    cid = request.form.get('cid')
                    # _, response = Config.app.system.admin.agents.user.auth.delete_chat(uid, gid, cid)
                    return jsonify({"response": "Removing chat", "uid": uid})

                    if _:
                        response_data = {'status': 'success',
                                         'message': response}
                        return jsonify(response_data)

                except Exception as e:
                    self.handle_error(e)
                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)

            @self.app.route("/create_group", methods=['POST'])
            def create_group():
                try:
                    uid = request.form.get('uid')
                    group_name = request.form.get('name')
                    group_description = request.form.get('description')
                    group_date = request.form.get('date')
                    _, response = Config.app.system.admin.agents.user.auth.create_group(user_id=uid,
                                                                                        group_name=group_name, date=group_date)
                    if _:
                        response_data = {'status': 'success',
                                         'message': response[0]}
                        self.socketio.emit("update_group_list", response[1])

                    return jsonify(response_data)

                except Exception as e:
                    self.handle_error(e)
                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)

            @self.app.route("/edit_group", methods=['POST'])
            def edit_group():
                try:
                    uid = request.form.get('uid')
                    gid = request.form.get('gid')
                    # _, response = Config.app.system.admin.agents.user.auth.delete_group(uid, gid)
                    return jsonify({"response": "Edit group", "uid": uid})

                    if _:
                        response_data = {'status': 'success',
                                         'message': response}
                        return jsonify(response_data)

                except Exception as e:
                    self.handle_error(e)
                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)

            @self.app.route("/delete_group", methods=['POST'])
            def delete_group():
                try:
                    uid = request.form.get('uid')
                    gid = request.form.get('gid')
                    _, response = Config.app.system.admin.agents.user.auth.delete_group(
                        uid, gid)
                    return jsonify({"response": "Removing group", "uid": uid})

                    if _:
                        response_data = {'status': 'success',
                                         'message': response}
                        return jsonify(response_data)

                except Exception as e:
                    self.handle_error(e)
                    response_data = {'status': 'error',
                                     'message': 'Error processing the request'}
                    return jsonify(response_data)
        except Exception as e:
            self.handle_error(e)

    def process_responses(self):
        try:
            while not self.stop_flag:
                ids, data = self.queue_handler.get_queue(
                    "WEB_API_RESPONSE", 0.1, (None, None))
                if ids is None:
                    continue

                ssid = ids[0]
                did = ids[1]
                try:
                    # Send the response to all sockets associated with the session ID
                    if ssid in self.sessions:
                        for xids in self.sessions[ssid]:
                            if xids[1] == did:
                                self.socketio.emit(
                                    "chat_response", data, room=xids[0])
                            else:
                                self.socketio.emit(
                                    "chat_response", f"{data}", room=xids)
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue(
                        "CONSOLE", (self.name, f"ERROR while trying to respond to {ids} request. {e}"))
                    self.queue_handler.add_to_queue(
                        "LOGGING", (self.name, (e, traceback_str)))
        except Exception as e:
            self.handle_error(e)

    def main(self):
        try:
            self.event.wait()
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])
            self.register_routes()
            self.socketio.run(self.app, host="0.0.0.0",
                              port=8020, allow_unsafe_werkzeug=True)
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "API IS RUNNING"))
        except Exception as e:
            self.handle_error(e)

    def run(self):
        self.event.set()

    def _handle_system_ready(self):
        self.response_thread = threading.Thread(
            target=self.process_responses, name=f"{self.name}_RESPONSES")
        self.response_thread.start()
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
