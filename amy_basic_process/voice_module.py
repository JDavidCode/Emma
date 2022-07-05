# BasePythonLibraries
import time
# ImportedPythonLibraries
import pyaudio as pya
from vosk import Model, KaldiRecognizer
import speech_recognition as sr
import pyttsx3

eng = pyttsx3.init()
engVoice = eng.getProperty('voices')
pyMic = pya.PyAudio()

# Online Voice Recognizer
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Offline Voice Recognizer
model = Model('resources/vosk_models/en-model')
rec = KaldiRecognizer(model, 16000)
stream = pyMic.open(format=pya.paInt16, channels=1,
                    rate=16000, input=True, frames_per_buffer=8192)

#################################################################################
#################################################################################
#################################################################################


class talkProcess:
    def __init__():
        pass

    def talk(text):
        eng.say(text)
        eng.runAndWait()
        return

    def engVoiceConfig():
        eng.setProperty('voice', engVoice[1].id)
        eng.setProperty('rate', 125)
        eng.setProperty('volume', 1)
        return 0


class ListenInBack:
    def __init__():
        pass

    def Listener():
        stream.start_stream()
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = rec.Result()
                result = result[14:-3]
                return result
            else:
                pass


'''
    def micConfig():
        with mic as source:
            recognizer.energy_threshold = 4000
            recognizer.dynamic_energy_threshold = True
            recognizer.adjust_for_ambient_noise(mic, duration=3)
        return 0

    def callback(self, recognizer, voice):
        __output = recognizer.recognize_google(voice)
        try: 
            print(__output)
        except sr.UnknownValueError:
            print("Emy could not understand you")
        except sr.RequestError as e:
            print("Could not request result from Speech Recognition service; {0}".format(e))
        except:
            pass

    def inBackOnline(self):
        __stopStream = recognizer.listen_in_background(mic, self.callback)
        while True: 
            time.sleep(0.8)
'''

#################################################################################
#################################################################################
#################################################################################

if __name__ == '__main__':
    pass
