import json
import threading
import openai
import emma.globals as EMMA_GLOBALS
import traceback

class GPT:
    def __init__(self, queue_handler, console_handler):
        openai.api_key = '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'
        self.console_handler = console_handler
        self.tag = "GPT"
        self.queue_handler = queue_handler
        self.stop_flag = False
        self.event = threading.Event()
        self.functions = EMMA_GLOBALS.tools_da.json_loader(
            path=EMMA_GLOBALS.stcpath_command_sch, json_type="list")

    def update_chat(self, user_id, session_id, message):
        path = f"emma/common/users/{user_id}_sessions.json"

        sessions = EMMA_GLOBALS.tools_da.json_loader(path, json_type="dict")

        try:
            sessions[session_id].append(message)
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))
            #manage unendintefied session
        with open(path, 'w') as file:
            json.dump(sessions, file, indent=4)

    def get_chat(self, user_id, session_id):
        path = f"emma/common/users/{user_id}_sessions.json"
        chat = EMMA_GLOBALS.tools_da.json_loader(
            path, i=session_id, json_type="list")
        
        if len(chat) >= 11:
            truncated_chat = [chat[0]] + chat[-10:]
        else:
            truncated_chat = chat
            
        return truncated_chat

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            ids, data = self.queue_handler.get_queue("GPT_INPUT", 0.1, (None, None))
            if ids is None:
                continue
            socket_id, session_id, user_id = ids
            message = {
                "role": "user",
                "content": f"{data}",
            }
            self.update_chat(user_id, session_id, message)
            chat = self.get_chat(user_id, session_id)

            if data == None or data == "":
                continue
            else:
                try:
                    response = openai.ChatCompletion.create(
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

                        self.queue_handler.add_to_queue("LOGGING", (self.tag, function_call))
                        self.queue_handler.add_to_queue(
                            'RESPONSE', ['funcall', [function_name, args], socket_id])

                        message = {
                            "role": "function",
                            "name": function_name,
                            "content": "The function has been executed",
                        }

                        self.update_chat(user_id, session_id, message)
                        #chat = self.get_chat(user_id, session_id)
                        #self.console_handler.write(self.tag, [user_id, message])

                        # Extend conversation with function response
                        #second_response = openai.ChatCompletion.create(
                        #    model="gpt-3.5-turbo-0613",
                        #   messages=chat,)
                        # get a new response from GPT where it can see the function response
                        #self.console_handler.write(self.tag, second_response["choices"][0]["message"]["content"])
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
                    self.queue_handler.add_to_queue("LOGGING", (self.tag, (t, traceback_str)))

                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue("LOGGING", (self.tag, (e, traceback_str)))

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True
