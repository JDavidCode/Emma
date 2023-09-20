import threading
import time
import keyboard
from app.config.config import Config


class HotKeys:
    """
    Class for managing hotkeys and event handling.

    Args:
        name (str): The name of the HotKeys instance.
        queue_name (str): The name of the queue.
        queue_handler: An object responsible for handling the queue.
        event_handler: An object responsible for event handling.
    """

    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.event_handler = event_handler
        self.queue_handler = queue_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False
        self.hotkey_ctrl_0 = None
        self.hotkey_ctrl_8 = None
        self.hotkey_ctrl_1 = None
        self.custom_hotkeys = {}

    def set_hotkeys(self):
        """Set predefined hotkeys."""
        self.hotkey_ctrl_0 = keyboard.add_hotkey(
            "ctrl+0", self.local_handle_shutdown)
        self.hotkey_ctrl_8 = keyboard.add_hotkey(
            "ctrl+8", self.handle_stop_task)
        self.hotkey_ctrl_1 = keyboard.add_hotkey("ctrl+1", self.handle_reload)

    def add_custom_hotkey(self, hotkey_combination, handler_function):
        """
        Add a custom hotkey with a specified handler function.

        Args:
            hotkey_combination (str): The hotkey combination (e.g., "ctrl+alt+X").
            handler_function (callable): The function to be called when the hotkey is triggered.
        """
        custom_hotkey = keyboard.add_hotkey(
            hotkey_combination, handler_function)
        self.custom_hotkeys[hotkey_combination] = custom_hotkey

    def remove_custom_hotkey(self, hotkey_combination):
        """
        Remove a custom hotkey by its hotkey combination.

        Args:
            hotkey_combination (str): The hotkey combination to be removed.
        """
        if hotkey_combination in self.custom_hotkeys:
            hotkey = self.custom_hotkeys[hotkey_combination]
            keyboard.remove_hotkey(hotkey)
            del self.custom_hotkeys[hotkey_combination]

    def pause_hotkey(self, hotkey_combination):
        """
        Pause a custom hotkey by its hotkey combination.

        Args:
            hotkey_combination (str): The hotkey combination to be paused.
        """
        if hotkey_combination in self.custom_hotkeys:
            hotkey = self.custom_hotkeys[hotkey_combination]
            hotkey.pause()

    def resume_hotkey(self, hotkey_combination):
        """
        Resume a custom hotkey by its hotkey combination.

        Args:
            hotkey_combination (str): The hotkey combination to be resumed.
        """
        if hotkey_combination in self.custom_hotkeys:
            hotkey = self.custom_hotkeys[hotkey_combination]
            hotkey.resume()

    def pause_all_hotkeys(self):
        """Pause all custom hotkeys and predefined hotkeys."""
        for hotkey in self.custom_hotkeys.values():
            hotkey.pause()
        self.hotkey_ctrl_0.pause()
        self.hotkey_ctrl_8.pause()
        self.hotkey_ctrl_1.pause()

    def resume_all_hotkeys(self):
        """Resume all custom hotkeys and predefined hotkeys."""
        for hotkey in self.custom_hotkeys.values():
            hotkey.resume()
        self.hotkey_ctrl_0.resume()
        self.hotkey_ctrl_8.resume()
        self.hotkey_ctrl_1.resume()

    def main(self):
        """Main method for the HotKeys instance."""
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instantiated"])
        self.event.wait()
        while not self.stop_flag:
            time.sleep(1)

    def local_handle_shutdown(self):
        """Handle local shutdown."""
        Config.app.system.admin.agents.sys.server_shutdown()

    def handle_reload(self):
        """Handle server reload."""
        Config.app.system.admin.agents.sys.server_restart()

    def handle_shutdown(self):
        """Handle shutting down the HotKeys instance."""
        keyboard.remove_hotkey(self.hotkey_ctrl_0)
        keyboard.remove_hotkey(self.hotkey_ctrl_8)
        keyboard.remove_hotkey(self.hotkey_ctrl_1)
        self.__stop()

    def handle_stop_task(self):
        """Handle stopping a task."""
        print("Stop task hotkey pressed")

    def attach_components(self, module_name):
        """
        Attach components from a specified module.

        Args:
            module_name (str): The name of the module to attach components from.
        """
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
        """Start the HotKeys instance."""
        self.set_hotkeys()
        self.event.set()
        self.queue_handler.add_to_queue("CONSOLE", [self.name, "Is Started"])

    def stop(self):
        """Stop the HotKeys instance."""
        self.stop_flag = True
