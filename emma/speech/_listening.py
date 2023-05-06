# BasePythonLibraries
import importlib
import os

# ImportedPythonLibraries
import pyaudio as pya
import vosk


class ListenInBack:
    def __init__(self, queue_manager, console_output):
        self.sys = importlib.import_module("emma.sys_v")
        dM = importlib.import_module("emma.data_module")
        vosk.SetLogLevel(-1)
        pyMic = pya.PyAudio()
        lang = os.environ["USERLANG"]
        model = vosk.Model("assets/models/vosk_models/{}-model".format(lang))
        self.user_lvl = os.environ["USERLVL"]
        self.rec = vosk.KaldiRecognizer(model, 16000)
        self.stream = pyMic.open(
            format=pya.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192,
        )
        self.console_output = console_output
        self.tag = "Voice Thread"
        self.db = dM.AmyData
        self.queue = queue_manager
        self.stop_flag = False

        self.run()

    def run(self):
        self.stream.start_stream()
        while not self.stop_flag:
            rec = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(rec):
                result = self.rec.Result()
                result = result[14:-3].lower()
                if result != "":
                    self.console_output.write(self.tag, result)
                    if "amy" in result:
                        result = result.replace("amy", "")
                        if result == "" or result == " ":
                            continue
                        if result[0] == " ":
                            result = result[1:]
                        if result[len(result) - 1] == " ":
                            result = result[:-1]
                        self.queue.add_to_queue("COMMANDS", result)
                        self.queue.add_to_queue("CURRENT_INPUT", result)

                        # Chat
                        e_ans = self.db.chat_indexer(result)
                        if result != e_ans and e_ans != None and e_ans != "":
                            self.queue.add_to_queue("TALKING", e_ans)

    def stop(self):
        self.stop_flag = True


"""
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
            print('Emy could not understand you')
        except sr.RequestError as e:
            print('Could not request result from Speech Recognition service; {0}'.format(e))
        except:
            pass

    def inBackOnline(self):
        __stopStream = recognizer.listen_in_background(mic, self.callback)
        while True: 
            time.sleep(0.8)
"""

if __name__ == "__main__":
    ListenInBack()
