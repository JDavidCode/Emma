import speech_recognition as SR
import pyttsx3

recognize = SR.Recognizer()
eng = pyttsx3.init()
engVoice = eng.getProperty("voices")


def engVoiceConfig():
    eng.setProperty("rate", 140) #Velocidad del Habla de la Maquina
    eng.setProperty("volume", 1) #Volumen de la maquina
    eng.setProperty("voice", engVoice[2].id) #Seleccion de Voz
    return(0)

def micConfig():
    with SR.Microphone() as source:
        recognize.energy_threshold = 4000   
        recognize.adjust_for_ambient_noise(source, duration=4)  
        recognize.dynamic_energy_threshold = True
        engVoiceConfig()
    return(0)

def talkP(text):
    eng.say(text)
    eng.runAndWait()
    return(0)

def voice():
    try:
        with SR.Microphone() as source:
            print('...')
            minput = recognize.listen(source)  #Entrada de mic / micInput
            recognizeOuput = recognize.recognize_google_cloud(minput, language="es-ES") # salida de texto
    except:
        talkP('No he entendido señor.')
        recognizeOuput = 'ErrorNRI'
    return(recognizeOuput)    