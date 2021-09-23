import speech_recognition as SR
import EmiDatabase.EmiDataConnect as bM
import pyttsx3

recognize = SR.Recognizer()
eng = pyttsx3.init()
engVoice = eng.getProperty("voices")


def engVoiceConfig():
    eng.setProperty("rate", 145) #Velocidad del Habla de la Maquina
    eng.setProperty("volume", 1) #Volumen de la maquina
    eng.setProperty("voice", engVoice[0].id) #Seleccion de Voz
    return(0)

def voiceProcess():
    with SR.Microphone() as source:
        while True:
            minput = recognize.listen(source)  #Entrada de mic / micInput
            recognizeOuput = recognize.recognize_google(minput, language="es-ES") # salida de texto
            bM.BDInput(recognizeOuput)
            return (recognizeOuput)

def talkP(text):
    eng.say(text)
    eng.runAndWait()
    return(0)

def micConfig():
    with SR.Microphone() as source:
        recognize.energy_threshold = 4000   
        recognize.adjust_for_ambient_noise(source, duration=5)  
        recognize.dynamic_energy_threshold = True
        engVoiceConfig()
    return(0)
