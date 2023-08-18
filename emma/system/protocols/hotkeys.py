import threading
import time
import keyboard
import emma.globals as EMMA_GLOBALS


class HOTKEYS:
    def __init__(self, name, queue_name, queue_handler, event_handler) -> None:
        self.name = name
        self.queue_name = queue_name
        self.event_handler = event_handler
        self.queue_handler = queue_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.hotkey_ctrl_0 = None
        self.hotkey_ctrl_8 = None
        self.custom_hotkeys = {}

    def set_hotkeys(self):
        self.hotkey_ctrl_0 = keyboard.add_hotkey(
            "ctrl+0", self.local_handle_shutdown)
        self.hotkey_ctrl_8 = keyboard.add_hotkey(
            "ctrl+8", self.handle_stop_task)
        self.hotkey_ctrl_1 = keyboard.add_hotkey("ctrl+1", self.handle_reload)

    def add_custom_hotkey(self, hotkey_combination, handler_function):
        custom_hotkey = keyboard.add_hotkey(
            hotkey_combination, handler_function)
        self.custom_hotkeys[hotkey_combination] = custom_hotkey

    def remove_custom_hotkey(self, hotkey_combination):
        if hotkey_combination in self.custom_hotkeys:
            hotkey = self.custom_hotkeys[hotkey_combination]
            keyboard.remove_hotkey(hotkey)
            del self.custom_hotkeys[hotkey_combination]

    def pause_hotkey(self, hotkey_combination):
        if hotkey_combination in self.custom_hotkeys:
            hotkey = self.custom_hotkeys[hotkey_combination]
            hotkey.pause()

    def resume_hotkey(self, hotkey_combination):
        if hotkey_combination in self.custom_hotkeys:
            hotkey = self.custom_hotkeys[hotkey_combination]
            hotkey.resume()

    def pause_all_hotkeys(self):
        for hotkey in self.custom_hotkeys.values():
            hotkey.pause()
        self.hotkey_ctrl_0.pause()
        self.hotkey_ctrl_8.pause()

    def resume_all_hotkeys(self):
        for hotkey in self.custom_hotkeys.values():
            hotkey.resume()
        self.hotkey_ctrl_0.resume()
        self.hotkey_ctrl_8.resume()

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
        self.event.wait()
        while not self.stop_flag:
            time.sleep(1)

    def local_handle_shutdown(self):
        EMMA_GLOBALS.sys_v.server_shutdown()

    def handle_reload(self):
        EMMA_GLOBALS.sys_v.server_restart()

    def handle_shutdown(self):
        keyboard.remove_hotkey(self.hotkey_ctrl_0)
        keyboard.remove_hotkey(self.hotkey_ctrl_8)
        self.stop()

    def handle_stop_task(self):
        print("Stop task hotkey pressed")
        
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
        self.set_hotkeys()
        self.event.set()
        self.queue_handler.add_to_queue("CONSOLE", [self.name, "Is Started"])

    def stop(self):
        self.stop_flag = True
