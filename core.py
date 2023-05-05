# BasePythonLibraries
import importlib
from threading import Thread
import time
import os


class Cluster:
    def __init__(self) -> None:
        # BASIC PROCESS IMPORTS
        self.sys = importlib.import_module("amy_basic_process.sys_v")
        self.listening = importlib.import_module("amy_basic_process.speech._listening")
        self.web_app = importlib.import_module("web_server.app")
        self.talking = importlib.import_module("amy_basic_process.speech._talking")
        self.trading = importlib.import_module("workers.trading_bots.supervisor")
        userPrefix, welcome = self.sys.awake().run()
        self.thread_manager = self.sys.ThreadManager()
        self.queue_manager = self.thread_manager.QueueManager()
        self.console_manager = self.thread_manager.ConsoleManager(self.queue_manager)
        self.thread_management()
        self.server_integrity()

    def thread_management(self):
        thread_manager = self.thread_manager
        queue_manager = self.queue_manager
        console_manager = self.console_manager

        # Create a Queue for CURRENTS
        queue_manager.create_queue("CURRENT_INPUT", 1)
        # Create a Queue for WBDATA
        queue_manager.create_queue("SERVERDATA", 1)
        # Create a Queue for CONSOLE
        queue_manager.create_queue("CONSOLE")
        # create a Queue for COMMANDS
        queue_manager.create_queue("COMMANDS")
        # create a Queue for TALKING
        queue_manager.create_queue("TALKING")

        # create CommandManager thread
        command_instance = self.sys.CommandsManager(
            queue_manager, console_manager, thread_manager
        )
        command_manager = Thread(
            target=command_instance,
            daemon=True,
        )
        thread_manager.add_thread(command_manager)
        # start the CommandManager thread
        thread_manager.start_thread("CommandsManager")

        # create listening thread
        voice_instance = self.listening.ListenInBack(queue_manager, console_manager)
        voice_thread = Thread(
            target=voice_instance,
            daemon=True,
        )
        thread_manager.add_thread(voice_thread)
        # thread_manager.start_thread("ListenInBack")  # start  listening thread

        # create talking thread
        talk_instance = self.talking.TalkInBack(queue_manager, console_manager)
        talk_thread = Thread(target=talk_instance, daemon=True)
        thread_manager.add_thread(talk_thread)
        thread_manager.start_thread("Talk")  # start  talking thread

        # create CommandManager thread
        app_instance = self.web_app.WebApp(queue_manager, console_manager)
        web_app_thread = Thread(
            target=app_instance,
            daemon=True,
        )
        thread_manager.add_thread(web_app_thread)
        # start the CommandManager thread
        thread_manager.start_thread("WebApp")
        # create Trading Bot thread
        bot_instance = self.trading.TradingSupervisor(console_manager)
        trading_thread = Thread(target=bot_instance, daemon=True)
        thread_manager.add_thread(trading_thread)
        thread_manager.start_thread("TradingSupervisor")  # start  Trading thread
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

    talk("Hola! Soy Amy tu asistente personal, ¿en que puedo ayudarte?")

    while True:
        question = transformar_audio_a_texto().lower()

        conversation += "\nYou: " + question + "\nAmy:"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=conversation,
            temperature=0.5,
            max_tokens=100,
            top_p=0.3,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["\n", " You:", " Amy:"]
        )
        answer = response.choices[0].text.strip()
        conversation += answer
        print("Amy: " + answer + "\n")
        talk(answer)
"""
