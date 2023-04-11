# BasePythonLibraries
import importlib
from dotenv import get_key as dotenv
import threading

# ImportedPythonLibraries
import pyaudio as pya
from vosk import Model, KaldiRecognizer


class ListenInBack:
    def __init__(self):
        self.sys = importlib.import_module('amy_basic_process.sys_v')
        dM = importlib.import_module('amy_basic_process.data_module')
        _talk = importlib.import_module('amy_basic_process.speech._talking')
        self.talk = _talk.TalkProcess.talk

        pyMic = pya.PyAudio()
        lang = dotenv(".venv/.env", "USERLANG")
        model = Model('assets/vosk_models/{}-model'.format(lang))
        self.user_lvl = dotenv(".venv/.env", "USERLVL")
        self.rec = KaldiRecognizer(model, 16000)
        self.stream = pyMic.open(format=pya.paInt16, channels=1,
                                 rate=16000, input=True, frames_per_buffer=8192)
        self.console_output = self.sys.ThreadManager.ConsoleOutput()
        self.db = dM.AmyData
        self.run()

    def run(self):
        self.stream.start_stream()
        while True:
            rec = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(rec):
                result = self.rec.Result()
                result = result[14:-3].lower()
                if result != '':
                    self.console_output.write(f"point 1: {result}")
                    if "amy" in result:
                        result = result.replace('amy', '')
                        if result == "":
                            continue
                        if result[0] == " ":
                            result = result[1:]
                        elif result[len(result)-1] == " ":
                            result = result[:-1]

                        e_ans, task, data, key = self.db.task_indexer(
                            result, self.user_lvl)

                        # Task
                        if key == True:
                            if e_ans != "" and e_ans != None:
                                self.console_output.write(f"Amy Say: {e_ans}")
                                self.talk(e_ans)
                            try:
                                self.sys.CommandsManager(task, data)
                                continue
                            except Exception as e:
                                self.console_output.write(
                                    f"An exception ocurred while trying to execute: {task}")
                                self.console_output.write(
                                    f"Exception: {e}")
                                continue

                        # Chat
                        e_ans = self.db.chat_indexer(result)
                        if result != e_ans and e_ans != None and e_ans != "":
                            self.console_output.write(f"Amy Say: {e_ans}")
                            self.talk(e_ans)
                            continue

            else:
                continue


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

if __name__ == '__main__':
    ListenInBack()
