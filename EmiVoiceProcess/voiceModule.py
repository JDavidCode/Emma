import speech_recognition as sr
import pyttsx3

recognize = sr.Recognizer()
eng = pyttsx3.init()
engVoice = eng.getProperty("voices")

def engVoiceConfig():
    eng.setProperty("rate", 160) #Velocidad del Habla de la Maquina
    eng.setProperty("volume", 1) #Volumen de la maquina
    eng.setProperty("voice", engVoice[0].id) #Seleccion de Voz
    return(0)

def voiceProcess():
    with sr.Microphone() as source:
        print("Escuchando")
        minput = recognize.listen(source)  #Entrada de mic / micInput
        recognizeOuput = recognize.recognize_google(minput, language="es-ES") # salida de texto
        print(recognizeOuput)
        while recognizeOuput == recognizeOuput:
            recognizeOuput = voiceProcess()
    return (recognizeOuput)

def talkProcess(text):
    eng.say(text)
    eng.runAndWait()
    return(0)

def micConfig():
    with sr.Microphone() as source:
        recognize.energy_threshold = 4000   
        recognize.adjust_for_ambient_noise(source, duration=5)  
        recognize.dynamic_energy_threshold = True
        voiceProcess()
    return(0)
