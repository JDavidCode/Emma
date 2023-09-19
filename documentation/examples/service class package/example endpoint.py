import importlib
import threading


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
        # Subscribe itself to the EventHandler
        self.event_handler.subscribe(self)

    def main(self):
        pass  # SERVICE/PLUGIN/APP enpoint here the app start when the thread start

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

    def handle_shutdown(self):  # This for event handling
        self.stop_flag = False

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True
