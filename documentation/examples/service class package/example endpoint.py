import importlib
import threading
import traceback


class myclass:
    def __init__(self, name, queue_name, queue_handler, event_handler, thread_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.thread_handler = thread_handler
        self.thread_utils = importlib.import_module(
            "system.utils._attach").Attach()
        self.event_handler.subscribe(self)

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
        self.event.wait()

        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])

        while not self.stop_flag:
            # CLASS MAIN LOGIC HERE
            continue

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

    def stop(self):
        self.stop_flag = True

    def handle_error(self, error, message=None):
        error_message = f"Error in {self.name}: {error}"
        if message:
            error_message += f" - {message}"
        traceback_str = traceback.format_exc()
        self.queue_handler.add_to_queue("LOGGING", (self.name, traceback_str))

    def handle_shutdown(self):  # This for event handling
        self.stop_flag = False
