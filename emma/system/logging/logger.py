import threading
import json
import datetime
import emma.globals as EMMA_GLOBALS
import traceback
import os


class Logger:
    def __init__(self, queue_handler, event_handler):
        self.tag = "LOGGER"
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.log_buffer = LogBuffer()

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            remitent, output = self.queue_handler.get_queue('LOGGING')
            dateTime = datetime.datetime.now()
            clock = dateTime.time()
            log_entry = {
                "timestamp": dateTime.isoformat(),
                "remitent": remitent,
                "output": output,
            }
            self.save_log(log_entry)  # Add the log entry to the buffer

    def save_log(self, log_entry):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(module_dir)
        date = datetime.datetime.now().strftime("%Y-%m-%d")  # Get the current date in the format "YYYY-MM-DD"
        history_dir = os.path.join(parent_dir, "logging", "history")  # Relative folder path
        log_path = os.path.join(history_dir, f"{date}.json")

        if not os.path.exists(history_dir):
            # Create the directory if it doesn't exist
            os.makedirs(history_dir)

        if not os.path.exists(log_path):
            # Create the file if it doesn't exist
            with open(log_path, "w") as f:
                json.dump([], f, indent=4)  # Initialize the JSON file as an empty list

        self.log_buffer.set_log_path(log_path)  # Set the log_path before appending log entries
        self.log_buffer.append(log_entry) 

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.queue_handler.add_to_queue("LOGGING", ("LOGGER", "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(self)  # put it when ready for shutdown
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (e, traceback_str))


class LogBuffer:
    def __init__(self):
        self.log_path = None
        self.buffer = []
        self.buffer_size = 10  # Set the buffer size as desired, adjust if necessary

    def set_log_path(self, log_path):
        self.log_path = log_path

    def append(self, log_entry):
        self.buffer.append(log_entry)
        if len(self.buffer) >= self.buffer_size:
            self.flush_buffer()

    def flush_buffer(self):
        with open(self.log_path, "a") as log_file:
            for log_entry in self.buffer:
                log_file.write(json.dumps(log_entry) + "\n")
            self.buffer.clear()




if __name__ == "__main__":
    pass