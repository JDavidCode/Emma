# BasePythonLibraries
import time
import emma.config.globals as EMMA_GLOBALS


class EMCLKX:
    def __init__(self) -> None:
        EMMA_GLOBALS.sys_v_sa.run()
        self.thread_handler = EMMA_GLOBALS.sys_v_th
        self.queue_handler = EMMA_GLOBALS.sys_v_th_qh
        self.console_handler = EMMA_GLOBALS.sys_v_th_ch
        self.server_integrity()

    def server_integrity(self):
        timer = 5000
        while True:
            json = EMMA_GLOBALS.sys_v.server_performance(
                self.thread_handler.get_thread_status()
            )
            self.queue_handler.add_to_queue("SERVERDATA", json)
            if timer >= 4999:
                # Sleep for a certain period of time before checking again
                thread_status = self.thread_handler.get_thread_status()
                for status in thread_status:
                    self.console_handler.write(
                        "Main Thread",
                        f"{str(status[0])} is active: {status[1]}",
                    )
                timer = 0
            timer += 1
            time.sleep(1)


if __name__ == "__main__":
    EMCLKX()
