# BasePythonLibraries
import os
import threading

# ImportedPythonLibraries
import pyaudio as pya
import vosk


class VoiceListener:
    def __init__(self, queue_manager, console_manager):
        vosk.SetLogLevel(-1)
        pyMic = pya.PyAudio()
        lang = os.environ.get("USERLANG")
        print(lang)
        model = vosk.Model(
            "emma/assets/models/vosk_models/{}-model".format(lang))
        self.user_lvl = os.environ.get("USERLVL")
        self.rec = vosk.KaldiRecognizer(model, 16000)
        self.stream = pyMic.open(
            format=pya.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192,
        )
        self.console_manager = console_manager
        self.tag = "Voice Thread"
        self.queue = queue_manager
        self.stop_flag = False
        self.event = threading.Event()

    def main(self):
        self.event.wait()
        self.stream.start_stream()
        while not self.stop_flag:
            rec = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(rec):
                result = self.rec.Result()
                result = result[14:-3].lower()
                if result != "":
                    self.console_manager.write(self.tag, result)
                    if "amy" in result:
                        result = result.replace("emma", "")
                        if result == "" or result == " ":
                            continue
                        if result[0] == " ":
                            result = result[1:]
                        if result[len(result) - 1] == " ":
                            result = result[:-1]
                        self.queue.add_to_queue("COMMANDS", result)
                        self.queue.add_to_queue("CURRENT_INPUT", result)

                        self.queue.add_to_queue("TALKING", result)

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True


if __name__ == "__main__":
    VoiceListener()
