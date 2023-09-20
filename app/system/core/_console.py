import datetime
import os
import threading


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
