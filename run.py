# BasePythonLibraries
import importlib
from threading import Thread
import time
import os


class Cluster:
    def __init__(self) -> None:
        # BASIC PROCESS IMPORTS
        self.sys = importlib.import_module("emma.sys_v")
        self.listening = importlib.import_module("emma.speech._listening")
        self.web_app = importlib.import_module("emma.web_server.app")
        self.talking = importlib.import_module("emma.speech._talking")
        self.trading = importlib.import_module("workers.trading_bots.supervisor")
        userPrefix, welcome = self.sys.awake().run()
        self.thread_manager = self.sys.ThreadManager()
        self.queue_manager = self.thread_manager.QueueManager()
        self.console_manager = self.thread_manager.ConsoleManager(self.queue_manager)
        self.run()
        self.server_integrity()

    def run(self):
        thread_manager = self.thread_manager
        queue_manager = self.queue_manager
        console_manager = self.console_manager
        config_file = "emma/config/config.yml"
        self.sys.MainProcess().initialize_threads(
            config_file, queue_manager, console_manager, thread_manager
        )
        time.sleep(3)

    def server_integrity(self):
        timer = 9000
        mainp = self.sys.MainProcess()
        while True:
            json = mainp.server_performance(self.thread_manager.get_thread_status())
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
            timer += 1
            self.console_manager.write("THREAD", "IS RUNNING")
            time.sleep(1)


if __name__ == "__main__":
    Cluster()


"""
    conversation = ""

    talk("Hola! Soy Emma tu asistente personal, ¿en que puedo ayudarte?")

    while True:
        question = transformar_audio_a_texto().lower()

        conversation += "\nYou: " + question + "\Emma:"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=conversation,
            temperature=0.5,
            max_tokens=100,
            top_p=0.3,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["\n", " You:", " Emma:"]
        )
        answer = response.choices[0].text.strip()
        conversation += answer
        print("Emma: " + answer + "\n")
        talk(answer)
"""
