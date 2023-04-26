from flask import Flask, jsonify, render_template, request


class WebApp:
    def __init__(self, queue_manager, console_output):
        self.app = Flask(__name__)
        self.queue = queue_manager
        self.console_output = console_output
        self.tag = "WEB_APP Thread"
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

        @self.app.route('/data')
        def get_data():
            # get the data from the queue_manager
            data = self.queue.get_queue("SERVERDATA")

            # return the data as a JSON response
            return jsonify(data)

        @self.app.route('/console')
        def get_console():
            data = {}
            # get the data from the queue_manager
            try:
                data = self.queue.get_queue("CONSOLE", 2)
            except:
                pass
            # return the data as a JSON response
            return jsonify(data)

    def host(self):
        try:
            self.app.run(host='192.168.1.6', port=3018)
            self.console_output.write(self.tag, "WEB SERVER LOADED")
        except Exception as e:
            self.console_output.write(self.tag, str(e))


if __name__ == "__main__":
    pass
