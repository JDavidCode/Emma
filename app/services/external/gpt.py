import json
import os
import threading
import openai
from app.config.config import Config
import traceback


class GPT:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.name = name
        self.queue_name = queue_name
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
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
            self.handle_error(e)

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
            Config.app.system.admin.agents.system.sys.create_new_worker(
                thread_name)

    def main(self):
        self.event.wait()
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Is Started"])
        while not self.stop_flag:
            ids, data, channel = self.queue_handler.get_queue(
                self.queue_name[0], 0.1, (None, None, None))
            if data == None or channel == None:
                continue
            else:
                message = {
                    "role": "user",
                    "content": f"{data}",
                }

            if channel == "TELEGRAM_API":
                chat = [message]
            elif channel == "WEB_API":
                session_id, user_id, chat_id, device_id = ids
                self.update_chat(user_id, session_id, message)
                chat = self.get_chat(user_id, session_id)
            else:
                continue

            if data is None or data == "":
                continue
            else:
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo-0125",
                        messages=chat,
                        max_tokens=400,
                        functions=self.functions,
                        function_call="auto",
                        temperature=0.3)

                    response = response.model_dump_json()
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
                            'GPT_RESPONSE', ['funcall', [function_name, ], ids, channel])

                        message = {
                            "role": "function",
                            "name": function_name,
                            "content": "The function has been executed",
                        }
                        if channel == "WEB_API":
                            self.update_chat(user_id, session_id, message)
                    else:
                        answer = response["choices"][0]["message"]["content"]
                        message = {
                            "role": "assistant",
                            "content": answer
                        }

                        if channel == "WEB_API":
                            self.update_chat(user_id, session_id, message)

                        if "Lo siento" not in answer and "I'm sorry" not in answer:
                            self.queue_handler.add_to_queue(
                                'GPT_RESPONSE', ['answer', answer, ids, channel])

                except TimeoutError as t:
                    self.queue_handler.add_to_queue(
                        'RESPONSE', ['s0offline', data, device_id])
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue(
                        "LOGGING", (self.name, (t, traceback_str)))

                except Exception as e:
                    self.handle_error(e)

    def run(self):
        self.event.set()

    def _handle_system_ready(self):
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


if __name__ == "__main__":
    pass
