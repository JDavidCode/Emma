# BasePythonLibraries
import os
import threading

# ImportedPythonLibraries
import pyaudio as pya
import vosk


class VoiceListener:
    def __init__(self, queue_handler, console_handler, system_events):
        vosk.SetLogLevel(-1)
        self.system_events = system_events
        self.system_events.subscribe(self)

        lang = os.environ.get("USERLANG")
        self.user_lvl = os.environ.get("USERLVL")
        try:
            pyMic = pya.PyAudio()
            model = vosk.Model(
                f"emma/assets/models/vosk_models/{lang}-model")
            self.rec = vosk.KaldiRecognizer(model, 16000)
            self.stream = pyMic.open(
                format=pya.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192,
            )
        except Exception as e:
            print(f"Unnable to initialize VoiceInstace ERROR: {e}")
            self.exit()
        self.console_handler = console_handler
        self.tag = "Voice Thread"
        self.queue = queue_handler
        self.stop_flag = False
        self.event = threading.Event()

    def main(self):
        self.event.wait()
        while not self.stop_flag:
            self.stream.start_stream()
            rec = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(rec):
                result = self.rec.Result()
                result = result[14:-3].lower()
                if result != "":
                    self.console_handler.write(self.tag, result)
                    if "emma" in result:
                        result = result.replace("emma", "").strip().lower()
                        result = result
                        self.console_handler.write(self.tag, result)
                        self.queue.add_to_queue("COMMANDS", result)
                        self.queue.add_to_queue("CURRENT_INPUT", result)

                        self.queue.add_to_queue("TALKING", result)
        self.stream.stop_stream()
        self.stream.close()

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True

    def exit(self):
        return

    def handle_shutdown(self):
        self.stop()
        self.exit()


if __name__ == "__main__":
    VoiceListener()
