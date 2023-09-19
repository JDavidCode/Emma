import json
import threading
import time
from app.config.config import Config

import traceback


class DYNA:
    def __init__(self, name, queue_name, queue_handler):
        self.api_key = '0763a06d9518979a20d4fa3b2b64b89c68a2d2cafc732a7b'
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.stop_flag = False
        self.event = threading.Event()

    def update_chat(self, user_id, session_id, message):
        path = f"emma/common/users/{user_id}_sessions.json"

        sessions = Config.tools.data.json_loader(path, json_type="dict")
        try:
            sessions[session_id].append(message)
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (user_id, session_id, message)))

        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))
            # manage unendintefied session
        with open(path, 'w') as file:
            json.dump(sessions, file, indent=4)

    def get_chat(self, user_id, session_id):
        path = f"emma/common/users/{user_id}_sessions.json"
        chat = Config.tools.data.json_loader(
            path, i=session_id, json_type="list")

        if len(chat) >= 11:
            truncated_chat = [chat[0]] + chat[-10:]
        else:
            truncated_chat = chat

        return truncated_chat

    def verify_overload(self):
        global coun
        lenght = Config.app.system.core.queue.get_queue_lenght(
            self.queue)  # need fix
        if lenght >= 100:
            self.queue_handler.add_to_queue(
                "CONSOLE", ("", "creating new worker"))
            current_thread = threading.current_thread()
            thread_name = current_thread.name
            Config.app.system.agents._sys.create_new_worker(thread_name)

    def main(self):
        firts = True
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instanciate"])

        self.event.wait()

        while not self.stop_flag:
            if not self.stop_flag and firts:
                self.queue_handler.add_to_queue(
                    "CONSOLE", [self.name, "Is Started"])
                firts = False

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    UID = '0763a06d9518979a20d4fa3b2b64b89c68a2d2cafc732a7b'
    url = f"https://api.dynapictures.com/designs/{UID}"
