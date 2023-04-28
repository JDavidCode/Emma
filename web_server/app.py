import json
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO


class WebApp:
    def __init__(self, queue_manager, console_output):
        self.app = Flask(__name__)
        self.queue = queue_manager
        self.console_output = console_output
        self.tag = "WEB_APP Thread"
        self.socketio = SocketIO(self.app)
        self.register_routes()
        self.host()

    def register_routes(self):
        @self.app.route("/")
        def home():
            return render_template("index.html")

        @self.app.route("/", methods=["POST"])
        def process_form():
            # Process the form data here
            data = request.form['text_input']
            self.queue.add_to_queue("CURRENT_INPUT", data)
            self.queue.add_to_queue("COMMANDS", data)
            # Return a JSON response with the data
            return jsonify({'result': 'success', 'data': data})

        @self.socketio.on('connect')
        def connect():
            with open('web_server\\json\\console_data.json', 'r') as f:
                jsoni = json.load(f)
                f.close()

            # emit the data to the client
            self.socketio.emit('connect', jsoni)

        @self.socketio.on('get_data')
        def get_data():
            data = self.queue.get_queue("SERVERDATA")

            # emit the data to the client
            self.socketio.emit('get_data', data)

        @self.socketio.on('get_console')
        def get_console():
            data = ""
            try:
                data = self.queue.get_queue("CONSOLE", 1)
                # Load the JSON file into a Python object
                with open('web_server\\json\\console_data.json', 'r') as f:
                    jsoni = json.load(f)
                    f.close()
                # Identify the list to which you want to add the string
                j = jsoni

                # Add the string to the list
                j.insert(len(j), data)
                # Save the updated Python object back to the JSON file
                with open('web_server\\json\\console_data.json', 'w') as f:
                    json.dump(j, f, indent=4)
                    f.close()

            except:
                pass
            # emit the data to the client
            self.socketio.emit('get_console', data)

    def host(self):
        try:
            self.socketio.run(self.app, host='192.168.1.3', port=3018)
            self.console_output.write(self.tag, "WEB SERVER LOADED")
        except Exception as e:
            self.console_output.write(self.tag, str(e))


class jsond:
    def __init__(self) -> None:
        self.run()

    def run(self):
        # Load the JSON file into a Python object
        with open('web_server\\json\\console_data.json', 'r') as f:
            data = json.load(f)

        # Identify the list to which you want to add the string
        my_list = data

        # Add the string to the list
        my_list.append('new string')

        # Save the updated Python object back to the JSON file
        with open('web_server\\json\\console_data.json', 'w') as f:
            json.dump(data, f)


if __name__ == "__main__":
    pass
