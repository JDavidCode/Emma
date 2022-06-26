#BasePythonLibraries
import time
import threading
from xml.dom.pulldom import parseString
#ImportedPythonLibraries
import pyaudio as pya
from vosk import Model, KaldiRecognizer
import speech_recognition as sr
import pyttsx3 
#AppLibraries
import data_module as dM


#################################################################################
#################################################################################
#################################################################################

eng = pyttsx3.init()
engVoice = eng.getProperty('voices')
pyMic = pya.PyAudio()

#Online Voice Recognizer
recognizer = sr.Recognizer()
mic = sr.Microphone()

#Offline Voice Recognizer
model = Model('vosk_models/en-model')
rec = KaldiRecognizer(model, 16000)
stream = pyMic.open(format=pya.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

#################################################################################
#################################################################################
#################################################################################


def engVoiceConfig():
    eng.setProperty('voice', engVoice[1].id)
    eng.setProperty('rate', 125)
    eng.setProperty('volume', 1)
    return 0

def micConfig():
    with mic as source:
        recognizer.energy_threshold = 4000
        recognizer.dynamic_energy_threshold = True
        recognizer.adjust_for_ambient_noise(mic, duration=3)
    return 0

def talkProcess(text):
    eng.say(text)
    stream.stop_stream()
    eng.runAndWait()
    stream.start_stream()
    return 

def callback(recognizer, voice):
    output = recognizer.recognize_google(voice)
    try: 
        dM.chat(output)
    except sr.UnknownValueError:
        print("Emy could not understand you")
    except sr.RequestError as e:
        print("Could not request result from Speech Recognition service; {0}".format(e))
    except:
        pass

def inBackOnline():
    stopStream = (recognizer.listen_in_background(mic, callback))
    while True: 
        time.sleep(0.8)

def inBackProcess():
    stream.start_stream()
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result=rec.Result()
            result=result[14:-3]
            dM.chat(result)
        else: 
            pass

#################################################################################
#################################################################################
#################################################################################

if __name__ == '__main__':
    pass
