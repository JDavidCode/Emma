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
        self.console_handler = console_handler
        self.tag = "Voice Listener Thread"
        self.queue = queue_handler
        self.init_recognizer()
        self.stop_flag = False
        self.event = threading.Event()

    def main(self):
        count = 60
        self.event.wait()
        while not self.stop_flag:
            self.stream.start_stream()
            rec = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(rec):
                result = self.recognizer.Result()
                result = result[14:-3].lower()
                if result != "":
                    self.console_handler.write(self.tag, result)
                    if "computadora" in result:
                        result = result.replace(
                            "computadora", "").strip().lower()

                        result = result.replace("'", "")
                        self.console_handler.write(self.tag, result)
                        self.queue.add_to_queue("COMMANDS", result)
                        self.queue.add_to_queue("CURRENT_INPUT", result)
                        self.queue.add_to_queue("TALKING", result)
                    count += 2
                count += 3

            if count == 1000:
                self.clear()
                count = 0
                self.init_recognizer()

        self.stream.stop_stream()
        self.stream.close()

    def init_recognizer(self):

        try:
            lang = os.environ.get('USERLANG')
            self.mic = pya.PyAudio()
            self.model = vosk.Model(
                f"emma/assets/models/vosk_models/{lang}-model")
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            self.stream = self.mic.open(
                format=pya.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192,
            )
        except Exception as e:
            print(f"Unnable to initialize VoiceInstace ERROR: {e}")
            self.exit()

    def clear(self):
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
        del self.model
        del self.recognizer

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
