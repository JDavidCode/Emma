import datetime
import os
import threading
import keyboard
from app.config.config import Config


class Console:
    def __init__(self, name, queue_name, queue_handler):
        """
        Initialize the Console object.

        Args:
            name (str): The name of the console.
            queue_name (str): The name of the queue to listen for messages.
            queue_handler: The queue handler for message retrieval.
        """
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event = threading.Event()
        self.stop_flag = False

    def main(self):
        """
        Start the main loop to display console messages.
        """
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instantiated"])
        self.event.wait()

        console_input = self.Input(self)

        input_thread = threading.Thread(
            target=console_input.active_terminal, name=f"{self.name} input_thread")
        input_thread.start()
        # console_input.set_hotkeys()

        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])
        while not self.stop_flag:
            remitent, output = self.queue_handler.get_queue("CONSOLE")
            self.display_message(remitent, output)

    def display_message(self, remitent, output):
        """
        Display a message in the console with a timestamp.

        Args:
            remitent (str): The sender of the message.
            output (str): The message content.
        """
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{current_time}] {remitent} | {output}"
        print(formatted_message)

    def handle_index(self, section_path):
        """
        Handle indexing to display attributes and methods of an instance.

        Args:
            instance_name (str): The name of the instance to index.
        """
        section_names = section_path.split('.')
        current_section = Config

        for section_name in section_names:
            try:
                current_section = getattr(current_section, section_name)
            except AttributeError:
                self.display_message(
                    "Error", f"Config section '{section_path}' not found.")
                return

        self.display_message(
            "Index", f"Attributes and methods of {section_path} section:")
        index = Config.tools.data.format_json(
            Config.inspect_config_section(current_section))
        self.display_message("Index", index)

    def clear_console(self):
        """
        Clear the console screen.
        """
        # For Windows
        if os.name == "nt":
            os.system("cls")
        # For Linux/Mac
        else:
            os.system("clear")

    def progress_bar(self, percentage):
        """
        Display a progress bar in the console.

        Args:
            percentage (float): The completion percentage of the progress bar.
        """
        bar_length = 30
        num_blocks = int(bar_length * percentage / 100)
        progress_bar = "#" * num_blocks + "-" * (bar_length - num_blocks)
        self.clear_console()
        self.display_message("Progress", f"[{progress_bar}] {percentage:.2f}%")

    def run(self):
        """
        Set the event to start the console.
        """
        self.event.set()

    def stop(self):
        """
        Stop the console.
        """
        self.stop_flag = True

    class Input:
        """
        Class for managing hotkeys and event handling.

        Args:
            name (str): The name of the HotKeys instance.
            queue_name (str): The name of the queue.
            queue_handler: An object responsible for handling the queue.
            event_handler: An object responsible for event handling.
        """

        def __init__(self, pa):
            self.pa = pa
            self.hotkey_ctrl_0 = None
            self.hotkey_ctrl_8 = None
            self.hotkey_ctrl_1 = None
            self.custom_hotkeys = {}

        def active_terminal(self):
            while True:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                try:
                    print("")
                    input_text = input(f"[{current_time}] >> ")
                    if input_text == "shutdown" or input_text == "exit":
                        self._handle_shutdown()
                    elif input_text.startswith("index "):
                        instance_name = input_text.split(" ")[1]
                        self.pa.handle_index(instance_name)
                    else:
                        self.display_message("Error", "Unknown command.")
                except:
                    pass

        def set_hotkeys(self):
            """Set predefined hotkeys."""
            self.hotkey_ctrl_0 = keyboard.add_hotkey(
                "ctrl+0", self._handle_shutdown)
            self.hotkey_ctrl_8 = keyboard.add_hotkey(
                "ctrl+8", self.handle_stop_task)
            self.hotkey_ctrl_1 = keyboard.add_hotkey(
                "ctrl+1", self.handle_reload)

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

        def _handle_shutdown(self):
            """Handle local shutdown."""
            Config.app.system.admin.agents.sys.server_shutdown()

        def handle_reload(self):
            """Handle server reload."""
            Config.app.system.admin.agents.sys.server_restart()

        def handle_shutdown(self):
            """Handle shutting down the HotKeys instance."""
            try:
                keyboard.remove_hotkey(self.hotkey_ctrl_0)
                keyboard.remove_hotkey(self.hotkey_ctrl_8)
                keyboard.remove_hotkey(self.hotkey_ctrl_1)
            except:
                pass
            self.__stop()

        def handle_stop_task(self):
            """Handle stopping a task."""
            print("Stop task hotkey pressed")
