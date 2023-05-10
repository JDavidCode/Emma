import os
import threading
import pyttsx3
import openai
# ATTENTION POSSIBLE CHANGE FROMM PYRRSX3 TO ESPEAK-NG
global conversation


class Talking:
    def __init__(self, queue_manager, console_manager):
        openai.api_key = "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"
        self.console_manager = console_manager
        self.tag = "Talk Thread"
        self.queue = queue_manager
        self.stop_flag = False
        self.event = threading.Event()
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Emma is a great help and can Assist with anything, She was created by Juan Anaya The Owner of CoffeNow Systems"}],
            max_tokens=10,
            temperature=0)

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            # Wait for a command to be put in the queue
            question = self.queue.get_queue("TALKING", 1)
            if question == None:
                continue
            else:
                key = self.queue.get_queue("ISTK", 1)
                if key:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": f"{question}"}],
                        max_tokens=150,
                        temperature=0)
                    answer = response["choices"][0]["message"]["content"]
                    self.console_manager.write(self.tag, f"Emma: {answer}")

                    tts = _TTS()
                    tts.start(answer)
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
        self.engine_voice_config()

    def start(self, text_):
        self.engine.say(text_)
        self.engine.runAndWait()

    def engine_voice_config(self):
        if self.lang == "en":
            self.engine.setProperty("voice", self.engVoice[1].id)
        elif self.lang == "es":
            self.engine.setProperty("voice", self.engVoice[0].id)
        else:
            print("A voice language is null please enter the index")
            for i in self.engVoice:
                print(i)
                self.engine.setProperty("voice", self.engVoice[input()].id)
        self.engine.setProperty("rate", 125)
        self.engine.setProperty("volume", 1)
