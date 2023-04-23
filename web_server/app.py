from flask import Flask, render_template, request


class WebApp:
    def __init__(self, queue_manager, console_output):
        self.app = Flask(__name__)
        self.queue = queue_manager.add_to_queue
        self.console_output = console_output
        self.tag = "WEB_APP Thread"
        self.register_routes()
        self.run()

    def register_routes(self):
        @self.app.route("/")
        def home():
            return render_template("index.html")

        @self.app.route("/", methods=["POST"])
        def process_form():
            text_input = request.form.get("text_input")
            self.queue("COMMANDS", text_input)
            return render_template("index.html")

    def run(self):
        try:
            self.app.run(host='127.0.0.10', port=8000)
            self.console_output.write(self.tag, "WEB SERVER LOADED")
        except Exception as e:
            self.console_output.write(self.tag, str(e))


if __name__ == "__main__":
    pass
