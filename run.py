# BasePythonLibraries
import time
import emma.config.globals as EMMA_GLOBALS


class EMCLKX:
    def __init__(self) -> None:
        # BASIC PROCESS IMPORTS
        self.EGLOBALS = EMMA_GLOBALS
        userPrefix, welcome = self.EGLOBALS.sys_v_sa.run()
        self.thread_handler = self.EGLOBALS.sys_v_th
        self.queue_handler = self.EGLOBALS.sys_v_th_qh
        self.console_handler = self.EGLOBALS.sys_v_th_ch
        self.run()
        self.server_integrity()

    def run(self):
        self.EGLOBALS.sys_v.verify_paths()

        self.EGLOBALS.sys_v.initialize_queues()
        self.EGLOBALS.sys_v.initialize_threads()
        package_list = [
            {"repository": "https://github.com/JDavidCode/Emma-Web_Server/releases/download/v1.0.0/web_server.zip", "package_name": "web_server"}]
        self.EGLOBALS.forge_server.run(package_list)
        self.EGLOBALS.sys_v.initialize_threads(forge=True)

        time.sleep(3)

    def server_integrity(self):
        timer = 9000
        while True:
            json = self.EGLOBALS.sys_v.server_performance(
                self.thread_handler.get_thread_status())
            self.queue_handler.add_to_queue("SERVERDATA", json)
            if timer >= 8990:
                # Sleep for a certain period of time before checking again
                thread_status = self.thread_handler.get_thread_status()
                for status in thread_status:
                    self.console_handler.write(
                        "Main Thread",
                        f"{str(status[0])} is active: {status[1]}",
                    )
                timer = 0
            timer += 10
            time.sleep(1)


if __name__ == "__main__":
    EMCLKX()
