# BasePythonLibraries
import time
import emma.config.globals as EMMA_GLOBALS


class EMCLKX:
    def __init__(self) -> None:
        # BASIC PROCESS IMPORTS
        self.EGLOBALS = EMMA_GLOBALS
        userPrefix, welcome = self.EGLOBALS.sys_v_sa.run()
        self.thread_manager = self.EGLOBALS.sys_v_tm
        self.queue_manager = self.EGLOBALS.sys_v_tm_qm
        self.console_manager = self.EGLOBALS.sys_v_tm_cm
        self.run()
        self.server_integrity()

    def run(self):
        self.EGLOBALS.sys_v_mp.initialize_queues()
        self.EGLOBALS.sys_v_mp.initialize_threads()
        self.EGLOBALS.sys_v_bp.verify_paths()
        time.sleep(3)

    def server_integrity(self):
        timer = 9000
        while True:
            json = self.EGLOBALS.sys_v_mp.server_performance(
                self.thread_manager.get_thread_status())
            self.queue_manager.add_to_queue("SERVERDATA", json)
            if timer >= 8990:
                # Sleep for a certain period of time before checking again
                thread_status = self.thread_manager.get_thread_status()
                for status in thread_status:
                    self.console_manager.write(
                        "Main Thread",
                        f"{str(status[0])} is active: {status[1]}",
                    )
                timer = 0
            timer += 10
            time.sleep(1)


if __name__ == "__main__":
    EMCLKX()
