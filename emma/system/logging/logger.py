import importlib
import os
import time
import traceback
import datetime
import threading
import json


class Logger:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.thread_utils = importlib.import_module(
            "emma.system.utils.thread_utils").ThreadUtils()
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.log_buffer = LogBuffer()

    def main(self):
        first = True
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
        self.event.wait()

        while not self.stop_flag:
            if not self.stop_flag and first:
                self.queue_handler.add_to_queue(
                    "CONSOLE", [self.name, "Is Started"])
                first = False

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
        # Get the current date in the format "YYYY-MM-DD"
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        history_dir = os.path.join(
            parent_dir, "logging", "history")  # Relative folder path
        log_path = os.path.join(history_dir, f"{date}.txt")

        if not os.path.exists(history_dir):
            # Create the directory if it doesn't exist
            os.makedirs(history_dir)

        # Set the log path for the log buffer
        self.log_buffer.set_log_path(log_path)

        # Append the log entry to the log buffer
        self.log_buffer.append(log_entry)

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True

    def handle_shutdown(self):
        try:
            # Handle shutdown logic here
            self.queue_handler.add_to_queue(
                "LOGGING", ("LOGGER", "Handling shutdown..."))
            time.sleep(15)
            self.event_handler.subscribers_shutdown_flag(
                self)  # put it when ready for shutdown
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (e, traceback_str))

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


class LogBuffer:
    def __init__(self):
        self.log_path = None
        self.buffer = []
        self.buffer_size = 1  # Set the buffer size as desired, adjust if necessary

    def set_log_path(self, log_path):
        self.log_path = log_path

    def append(self, log_entry):
        # Convert the traceback to a string representation
        if isinstance(log_entry["output"], Exception):
            log_entry["output"] = traceback.format_exc()

        self.buffer.append(log_entry)
        if len(self.buffer) >= self.buffer_size:
            self.flush_buffer()

    def flush_buffer(self):
        with open(self.log_path, "a") as log_file:
            for log_entry in self.buffer:
                log_entry = str(log_entry)
                # Replace '\\n' with actual newline
                log_entry = log_entry.replace('\\n', '\n')
                log_file.write(log_entry + "\n \n")
            self.buffer.clear()
