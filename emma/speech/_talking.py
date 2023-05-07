import os
import pyttsx3

# ATTENTION POSSIBLE CHANGE FROMM PYRRSX3 TO ESPEAK-NG


class Talk:
    def __init__(self, queue_manager, console_output):
        openai.apikey = "Key"
        self.console_output = console_output
        self.tag = "Talk Thread"
        self.queue = queue_manager
        self.stop_flag = False
        self.run()

    def run(self):
        while not self.stop_flag:
            # Wait for a command to be put in the queue
            question = self.queue.get_queue("TALKING")
                conversation = "" 
  
            conversation += "\nYou: " + question + "\Emma:" 
             response = openai.Completion.create( 
                 model="text-davinci-003", 
                 prompt=conversation, 
                 temperature=0.5, 
                 max_tokens=100, 
                 top_p=0.3, 
                 frequency_penalty=0.5, 
                 presence_penalty=0.0, 
                 stop=["\n", " You:", " Emma:"] ) 
             answer = response.choices[0].text.strip() 
             conversation += answer 
             self.console_output.write(self.tag, f"Emma: {answer}") 
  
             tts = _TTS()
             tts.start(conversation)
             del tts

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
