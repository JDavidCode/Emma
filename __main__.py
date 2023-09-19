import threading
import time
from app.config.config import Config


class ServerIntegrityThread(threading.Thread):
    def __init__(self, thread_handler, queue_handler):
        super().__init__()
        self.stop_flag = threading.Event()
        self.thread_handler = thread_handler
        self.queue_handler = queue_handler

    def run(self):
        timer = 0
        while not self.stop_flag.is_set():
            # Your server integrity logic here

            if timer >= 1000:
                self.log_thread_status()
                timer = 0
            timer += 1
            time.sleep(1)

    def log_thread_status(self):
        key, thread_status = self.thread_handler.get_thread_status()
        for status in thread_status:
            self.queue_handler.add_to_queue(
                "CONSOLE", ("Main Thread", f"{str(status[0])} is active: {status[1]}"))


class RUN:
    def __init__(self):
        self.event = threading.Event()
        self.server_thread = None

    def reload(self):
        Config.del_all_sections()
        self.event.clear()
        self.run()

    def stop(self):
        if self.server_thread:
            self.server_thread.stop_flag.set()

    def initialize(self):
        Config._init.run()
        self.thread_handler = Config.app.system.core.thread
        self.queue_handler = Config.app.system.core.queue
        self.console_handler = Config.app.system.core._console
        self.event.set()
        Config.app._app = self

    def run(self):
        self.initialize()
        self.server_thread = ServerIntegrityThread(
            self.thread_handler, self.queue_handler)
        self.server_thread.start()


if __name__ == "__main__":
    run_instance = RUN()
    run_instance.run()
