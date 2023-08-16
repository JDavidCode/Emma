import threading
import time
import keyboard
import emma.globals as EMMA_GLOBALS


class HOTKEYS:
    def __init__(self, queue_handler, event_handler) -> None:
        self.event_handler = event_handler
        self.queue_handler = queue_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.tag = "HOTKEY PROTOCOLS"
        self.stop_flag = False
        self.hotkey_ctrl_0 = None
        self.hotkey_ctrl_8 = None

    def set_hotkeys(self):
        self.hotkey_ctrl_0 = keyboard.add_hotkey("ctrl+0", self.local_handle_shutdown)
        self.hotkey_ctrl_8 = keyboard.add_hotkey("ctrl+8", self.handle_stop_task)


    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.tag, "Has been instanciate"])
        self.event.wait()
        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.tag, "Is Started"])
        while not self.stop_flag:
            time.sleep(1)

    def local_handle_shutdown(self):
        EMMA_GLOBALS.sys_v.server_shutdown()

    def handle_shutdown(self):
        keyboard.remove_hotkey(self.hotkey_ctrl_0)
        keyboard.remove_hotkey(self.hotkey_ctrl_8)
        self.stop()

    def handle_stop_task(self):
        print("Stop task hotkey pressed")

    def run(self):
        self.set_hotkeys()
        self.event.set()

    def stop(self):
        self.stop_flag = True
