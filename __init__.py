import sys
import subprocess

PipList = ["pyttsx3", "vosk", "pyaudio", "pycaw", "TextBlob", "Pandas", "NumPy", "matplotlib", "scipy", "opencv-python",
           "opencv-contrib-python", "youtube-dl", "PyAutoGUI", "flask", "mysql-connector-python", "python-dotenv"]


def run():
    # implement pip as a subprocess:
    for i in PipList:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', i])

    # process output with an API in the subprocess module:
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
    print(installed_packages)


if __name__ == "__main__":
    run()
