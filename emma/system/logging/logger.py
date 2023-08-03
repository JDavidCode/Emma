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
            self.save_log(log_entry)

    def save_log(self, log_entry):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(module_dir)
        date = EMMA_GLOBALS.task_msc.date_clock(2)
        history_dir = os.path.join(parent_dir, "logging", "history")  # Relative folder path
        log_path = os.path.join(history_dir, f"{date}.json")

        if not os.path.exists(history_dir):
            # Create the directory if it doesn't exist
            os.makedirs(history_dir)
        if not os.path.exists(log_path):
            # Create the file if it doesn't exist
            with open(log_path, "w") as f:
                json.dump({}, f, indent=4)
            f.close()
        with open(log_path, "a") as log_file:
            log_file.write(json.dumps(log_entry) + "\n")

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.queue_handler.add_to_queue("LOGGING", ("LOGGER", "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(self)#put it when ready for shutdown
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (e, traceback_str))
