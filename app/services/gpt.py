import json
import threading
import time
import openai
from app.config.config import Config
import traceback


class GPT:
    def __init__(self, name, queue_name, queue_handler):
        openai.api_key = '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'
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.stop_flag = False
        self.event = threading.Event()
        self.functions = Config.tools.data.json_loader(
            path=Config.paths._command_sch, json_type="list")

    def update_chat(self, user_id, session_id, message):
        path = f"./app/common/users/{user_id}_sessions.json"

        sessions = Config.tools.data.json_loader(path, json_type="dict")
        try:
            sessions[session_id].append(message)
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (user_id, session_id, message)))

        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))
            # manage unidentified session
        with open(path, 'w') as file:
            json.dump(sessions, file, indent=4)

    def get_chat(self, user_id, session_id):
        path = f"./app/common/users/{user_id}_sessions.json"
        chat = Config.tools.data.json_loader(
            path, i=session_id, json_type="list")

        if len(chat) >= 11:
            truncated_chat = [chat[0]] + chat[-10:]
        else:
            truncated_chat = chat

        return truncated_chat

    def verify_overload(self):
        global coun  # Global variable 'coun' is not defined
        length = Config.app.system.core.queue.get_queue_length(
            self.queue)  # 'coun' is not defined; changed to 'length'
        if length >= 100:
            self.queue_handler.add_to_queue(
                "CONSOLE", ("", "creating a new worker"))
            current_thread = threading.current_thread()
            thread_name = current_thread.name
            Config.app.system.agents.sys.create_new_worker(thread_name)

    def main(self):
        first = True
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instantiated"])

        self.event.wait()

        while not self.stop_flag:
            if not self.stop_flag and first:
                self.queue_handler.add_to_queue(
                    "CONSOLE", [self.name, "Is Started"])
                first = False

            ids, data = self.queue_handler.get_queue(
                self.queue_name, 0.1, (None, None))

            if ids is None:
                continue
            socket_id, session_id, user_id = ids
            message = {
                "role": "user",
                "content": f"{data}",
            }
            self.update_chat(user_id, session_id, message)
            chat = self.get_chat(user_id, session_id)

            if data is None or data == "":
                continue
            else:
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo-0613",
                        messages=chat,
                        max_tokens=120,
                        functions=self.functions,
                        function_call="auto",
                        temperature=0)

                    response = response.to_dict()
                    response = json.dumps(response)
                    response = json.loads(response)

                    # Access the 'function_call' dictionary inside the 'message' dictionary
                    function_call = response["choices"][0]["message"].get(
                        "function_call")

                    # Check if 'function_call' exists and is a dictionary
                    if function_call and isinstance(function_call, dict):
                        function_name = function_call.get("name")
                        if function_call.get("arguments") != '{':
                            args = function_call.get("arguments")
                            if args.strip() == '{}':  # Check if args is an empty dictionary
                                args = {}
                            else:
                                args = json.loads(args)
                        else:
                            args = {}

                        self.queue_handler.add_to_queue(
                            "LOGGING", (self.name, function_call))

                        self.queue_handler.add_to_queue(
                            'RESPONSE', ['funcall', [function_name, args], socket_id])

                        message = {
                            "role": "function",
                            "name": function_name,
                            "content": "The function has been executed",
                        }

                        self.update_chat(user_id, session_id, message)
                    else:
                        answer = response["choices"][0]["message"]["content"]
                        message = {
                            "role": "assistant",
                            "content": answer
                        }

                        self.update_chat(user_id, session_id, message)

                        if "Lo siento" not in answer and "I'm sorry" not in answer:
                            self.queue_handler.add_to_queue(
                                'RESPONSE', ['answer', answer, socket_id])

                except TimeoutError as t:
                    self.queue_handler.add_to_queue(
                        'RESPONSE', ['s0offline', data, socket_id])
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue(
                        "LOGGING", (self.name, (t, traceback_str)))

                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue(
                        "LOGGING", (self.name, (e, traceback_str)))

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True
