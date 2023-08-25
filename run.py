# BasePythonLibraries
import threading
import time
from emma.config.config import Config


class EMCLKX:
    def __init__(self) -> None:
        self.event = threading.Event()  # Initialize the event attribute
        self.stop_flag = False
        self.run()

    def server_integrity(self):
        timer = 1000
        self.event.wait()

        while not self.stop_flag:
            json = Config.system.core.sys_variations.server_performance(
                self.thread_handler.get_thread_status()
            )

            if timer >= 1000:
                key, thread_status = self.thread_handler.get_thread_status()
                for status in thread_status:
                    self.queue_handler.add_to_queue(
                        "CONSOLE", ("Main Thread", f"{str(status[0])} is active: {status[1]}"))
                timer = 0
            timer += 1
            time.sleep(1)

    def reload(self):
        Config.instance.reset_globals()
        self.event.clear()
        self.run()

    def stop(self):
        self.stop_flag = True

    def run(self):
        Config.Awake.run()
        self.thread_handler = Config.system.core.thread
        self.queue_handler = Config.system.core.queue
        self.console_handler = Config.system.core._console
        self.event.set()  # Set the event to indicate readiness
        Config.system.app = self
        self.server_integrity()



if __name__ == "__main__":
    EMCLKX()
