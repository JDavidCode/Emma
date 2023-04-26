import sys
import os
import subprocess
import core


class CommandAwake:
    PipList = ["pyttsx3", "vosk", "pyaudio", "pycaw", "TextBlob", "Pandas", "NumPy", "matplotlib", "scipy", "opencv-python",
               "opencv-contrib-python", "youtube-dl", "PyAutoGUI", "flask", "flask_socketio", "mysql-connector-python", "python-dotenv", "imutils", "img2pdf", "psutil"]

    DirsStructure = [".AmyRootUser\\", ".AmyRootUser\\.preferences", ".AmyRootUser\\.temp",
                     ".AmyRootUser\\disk",  ".AmyRootUser\\disk\\user", ".AmyRootUser\\disk\\apps",
                     ".AmyRootUser\\disk\\home\\recycler", ".AmyRootUser\\disk\\home\\documents",
                     ".AmyRootUser\\disk\\home\\music", ".AmyRootUser\\disk\\home\\pictures",
                     ".AmyRootUser\\disk\\home\\videos"]

    def __init__(self):
        CommandAwake.install_packages()
        CommandAwake.create_dirs()
        core.cluster()

    def create_dirs():
        print("verifying directories")
        paths = CommandAwake.DirsStructure
        for i in paths:
            os.makedirs(i)

    def install_packages():
        print("verifying packages")
        PipList = CommandAwake.PipList
        # implement pip as a subprocess:
        for i in PipList:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', i])

        # process output with an API in the subprocess module:
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        print(installed_packages)


if __name__ == "__main__":
    CommandAwake()
