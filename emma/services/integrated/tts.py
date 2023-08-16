import os
import pyttsx3
import wave


class TTS:
    engine = None
    rate = None

    def __init__(self):
        self.tag = "TTS"
        self.lang = os.environ["USERLANG"]
        self.engine = pyttsx3.init()
        self.output_file = 'ox02da.wav'
        self.engVoice = self.engine.getProperty("voices")
        self.engine_voice_config()

    def convert(self, text):
        self.engine.save_to_file(text, self.output_file)
        self.engine.runAndWait()
        self.engine.stop()

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


if __name__ == "__main__":
    pass
