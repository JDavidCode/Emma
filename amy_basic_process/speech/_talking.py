from dotenv import get_key as dotenv
import pyttsx3
import pyaudio as pya

lang = dotenv(".venv/.env", "USERLANG")
eng = pyttsx3.init()
engVoice = eng.getProperty('voices')
pyMic = pya.PyAudio()


class talkProcess:
    def __init__():
        talkProcess.engVoiceConfig()

    def talk(text):
        eng.say(text)
        eng.runAndWait()
        return

    def engVoiceConfig():
        if lang == 'en':
            eng.setProperty('voice', engVoice[1].id)
        elif lang == 'es':
            eng.setProperty('voice', engVoice[2].id)
        else:
            print("A voice language is null please enter the index")
            for i in engVoice:
                print(i)
                eng.setProperty('voice', engVoice[input()].id)
        eng.setProperty('rate', 125)
        eng.setProperty('volume', 1)
        return 0
