import datetime
import os
import threading
import traceback
import keyboard
from app.config.config import Config


class Console:
    def __init__(self, name, queue_name, queue_handler, event_handler):
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
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.event = threading.Event()
        self.stop_flag = False

    def main(self):
        """
        Start the main loop to display console messages.
        """
        self.event.wait()
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
        self.event.set()

    def _handle_system_ready(self):
        console_input = self.Input(self)
        input_thread = threading.Thread(
            target=console_input.active_terminal, name=f"{self.name} input_thread")
        input_thread.start()
        self.run()
        return True

    def stop(self):
        self.stop_flag = True

    def handle_error(self, error, message=None):
        error_message = f"Error in {self.name}: {error}"
        if message:
            error_message += f" - {message}"
        traceback_str = traceback.format_exc()
        self.queue_handler.add_to_queue("LOGGING", (self.name, traceback_str))

    def _handle_shutdown(self):
        try:
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)
        except Exception as e:
            self.handle_error(e)

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

        def active_terminal(self):
            while True:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                try:
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

        def handle_reload(self):
            """Handle server reload."""
            Config.app.system.admin.agents.sys.server_restart()

        def handle_stop_task(self):
            """Handle stopping a task."""
            print("Stop task hotkey pressed")

        def _handle_system_ready(self):
            return True
        
        def handle_error(self, error, message=None):
            error_message = f"Error in {self.name}: {error}"
            if message:
                error_message += f" - {message}"
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, traceback_str))

        def _handle_shutdown(self):
            try:
                self.queue_handler.add_to_queue(
                    "CONSOLE", (self.name, "Handling shutdown..."))
                self.pa.event_handler.subscribers_shutdown_flag(
                    self)
            except Exception as e:
                self.handle_error(e)
