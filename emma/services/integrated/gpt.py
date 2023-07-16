import json
import threading
import openai
import emma.config.globals as EMMA_GLOBALS
global conversation


class GPT:
    def __init__(self, queue_handler, console_handler):
        openai.api_key = "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"
        self.console_handler = console_handler
        self.tag = "GPT"
        self.queue_handler = queue_handler
        self.stop_flag = False
        self.event = threading.Event()
        self.functions = EMMA_GLOBALS.tools_da.json_loader(
            path=EMMA_GLOBALS.stcpath_command_sch, json_type="list")

    def main(self):
        self.event.wait()
        messages = [{"role": "system", "content": "Youre Emma, Emma is a optimist and cheerful, can Assist with anything, She was created by Juan Anaya The Owner of CoffeNow Systems, here you have some rules: if you not understand the user ask you not answer. -if the user is asking for a task that require methods that you cant access like device's interface, physical actions, sentiments, etc. you not answer. -If you no have context not answer"}]
        while not self.stop_flag:
            question = self.queue_handler.get_queue("GPT_INPUT")

            if question == None or question == "":

                continue
            else:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-0613",
                        messages=[
                            {"role": "user", "content": f"{question}"}],
                        max_tokens=150,
                        functions=self.functions,
                        function_call="auto",
                        stop="\n",
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
                        args = function_call.get("arguments")

                        self.queue_handler.add_to_queue(
                            'RESPONSE', [True, [args, function_name]])

                        self.console_handler.write(
                            self.tag, [args, function_name])
                        messages.append(
                            {
                                "role": "function",
                                "name": function_name,
                                "content": "Executed",
                            }
                        )

                        # Extend conversation with function response
                        second_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo-0613",
                            messages=messages,
                        )
                        # get a new response from GPT where it can see the function response
                        self.console_handler.write(
                            self.tag, second_response["choices"][0]["message"]["content"])
                    else:
                        answer = response["choices"][0]["message"]["content"]
                        self.console_handler.write(self.tag, f"Emma: {answer}")
                        messages.append(
                            {
                                "role": "assistant",
                                "content": "answer",
                            }
                        )

                        if "Lo siento" not in answer and "I'm sorry" not in answer:
                            self.queue_handler.add_to_queue(
                                'RESPONSE', [False, answer])
                except Exception as e:
                    self.console_handler.write(self.tag, e)

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True
