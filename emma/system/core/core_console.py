import datetime
import os
import threading


class ConsoleHandler:
    def __init__(self, name, queue_name, queue_handler):
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        dateTime = datetime.datetime.now()
        self.event = threading.Event()

        clock = dateTime.time()
        self.clock = clock.strftime("%H:%M:%S")
        self.stop_flag = False

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])
        self.event.wait()
        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])
        while not self.stop_flag:
            remitent, output = self.queue_handler.get_queue("CONSOLE")
            print(f"[{self.clock}] {remitent} | {output}")

    def clear_console(self):
        # For Windows
        if os.name == "nt":
            os.system("cls")
        # For Linux/Mac
        else:
            os.system("clear")

    def progress_bar(self, percentage):
        bar_length = 30
        num_blocks = int(bar_length * percentage / 100)
        progress_bar = "#" * num_blocks + "-" * (bar_length - num_blocks)
        self.clear_console()
        self.write("Progress", f"[{progress_bar}] {percentage:.2f}%")

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True
