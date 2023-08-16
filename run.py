# BasePythonLibraries
import time
import emma.globals as EMMA_GLOBALS


class EMCLKX:
    def __init__(self) -> None:
        EMMA_GLOBALS.sys_awake.run()
        self.thread_handler = EMMA_GLOBALS.core_thread_handler
        self.queue_handler = EMMA_GLOBALS.core_queue_handler
        self.console_handler = EMMA_GLOBALS.core_console_handler
        self.server_integrity()

    def server_integrity(self):
        timer = 1000
        while True:
            json = EMMA_GLOBALS.sys_v.server_performance(
                self.thread_handler.get_thread_status()
            )

            if timer >= 20:
                key, thread_status = self.thread_handler.get_thread_status()
                for status in thread_status:
                    self.queue_handler.add_to_queue(
                        "CONSOLE", ("Main Thread", f"{str(status[0])} is active: {status[1]}"))
                timer = 0
            timer += 1
            time.sleep(1)


if __name__ == "__main__":
    EMCLKX()
