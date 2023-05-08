import os
import threading
import pyttsx3
import openai
# ATTENTION POSSIBLE CHANGE FROMM PYRRSX3 TO ESPEAK-NG


class Talking:
    def __init__(self, queue_manager, console_manager):
        self.gpt = openai.api_key = "<YOUR APY KEY FROM OPENAI ACCOUNT>"
        self.console_manager = console_manager
        self.tag = "Talk Thread"
        self.queue = queue_manager
        self.stop_flag = False
        self.event = threading.Event()

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            # Wait for a command to be put in the queue
            question = self.queue.get_queue("TALKING")

            if self.queue.get_queue("ISTK", 1):
                conversation = ""

                conversation += "\nYou: " + question + "\Emma:"
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=conversation,
                    temperature=0.5,
                    max_tokens=50,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6,
                    stop=["\n", " You:", " Emma:"])
                answer = response.choices[0].text.strip()
                conversation += answer
                self.console_manager.write(self.tag, f"Emma: {answer}")

                tts = _TTS()
                tts.start(conversation)
                del tts

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


class _TTS:
    engine = None
    rate = None

    def __init__(self):
        self.lang = os.environ["USERLANG"]
        self.engine = pyttsx3.init()
        self.engVoice = self.engine.getProperty("voices")

    def start(self, text_):
        self.engine.say(text_)
        self.engine.runAndWait()

    def engine_voice_config(self):
        if self.lang == "en":
            self.engine.setProperty("voice", self.engVoice[1].id)
        elif self.lang == "es":
            self.engine.setProperty("voice", self.engVoice[2].id)
        else:
            print("A voice language is null please enter the index")
            for i in self.engVoice:
                print(i)
                self.engine.setProperty("voice", self.engVoice[input()].id)
        self.engine.setProperty("rate", 125)
        self.engine.setProperty("volume", 1)
