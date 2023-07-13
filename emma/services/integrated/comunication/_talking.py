import os
import threading
import pyttsx3
import openai

global conversation


class Talking:
    def __init__(self, queue_handler, console_handler):
        openai.api_key = "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"
        self.console_handler = console_handler
        self.tag = "Talk Thread"
        self.queue = queue_handler
        self.stop_flag = False
        self.event = threading.Event()
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Emma is a great help and can Assist with anything, She was created by Juan Anaya The Owner of CoffeNow Systems, here you have some rules: if you not understand the user ask you not answer. -if the user is asking for a task that require methods that you cant access like device's interface, physical actions, sentiments, etc. you not answer. -If you no have context not answer"}],
            max_tokens=10,
            temperature=0)

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            # Wait for a command to be put in the queue
            question = self.queue.get_queue("TALKING", 1.5)
            if question == None:
                continue
            else:
                key = self.queue.get_queue("ISTK")
                try:
                    if key:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "user", "content": f"{question}"}],
                            max_tokens=150,
                            temperature=0)
                        answer = response["choices"][0]["message"]["content"]
                        self.console_handler.write(self.tag, f"Emma: {answer}")

                        if not "Lo siento" in answer:
                            tts = _TTS(self.console_handler)
                            tts.start(answer)
                            del tts
                except Exception as e:
                    self.console_handler.write(self.tag, e)

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


class _TTS:
    engine = None
    rate = None

    def __init__(self, console_handler):
        self.tag = "TTS"
        self.console_handler = console_handler
        self.lang = os.environ["USERLANG"]
        self.engine = pyttsx3.init()
        self.engVoice = self.engine.getProperty("voices")
        self.engine_voice_config()

    def start(self, text_):
        self.engine.say(text_)
        self.engine.runAndWait()

    def engine_voice_config(self):
        if self.lang == "en":
            for voice in self.engVoice:
                if voice.languages == [b'\x02en-us']:
                    self.engine.setProperty('voice', voice.id)
                else:
                    self.engine.setProperty('voice', self.engVoice[0].id)

        elif self.lang == "es":
            for voice in self.engVoice:
                if voice.languages == [b'\x05es-la']:
                    self.engine.setProperty('voice', voice.id)
                else:
                    self.engine.setProperty('voice', self.engVoice[1].id)
        else:
            print("A voice language is null please enter the index")
            for i in self.engVoice:
                print(i)
                self.engine.setProperty("voice", self.engVoice[input()].id)
        self.engine.setProperty("rate", 135)
        self.engine.setProperty("volume", 1)
