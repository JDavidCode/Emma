import sys
import os
import subprocess


class PackageInstaller:
    PipList = ["pyttsx3", "vosk", "pyaudio", "pycaw", "TextBlob", "Pandas", "NumPy", "matplotlib", "scipy", "opencv-python",  "pywhatkit",
               "opencv-contrib-python", "youtube-dl", "PyAutoGUI", "flask", "flask_socketio", "mysql-connector-python", "python-dotenv", "imutils", "img2pdf", "psutil"]

    DirsStructure = [".AmyRootUser\\", ".AmyRootUser\\.preferences", ".AmyRootUser\\.temp",
                     ".AmyRootUser\\disk",  ".AmyRootUser\\disk\\user", ".AmyRootUser\\disk\\apps",
                     ".AmyRootUser\\disk\\home\\recycler", ".AmyRootUser\\disk\\home\\documents",
                     ".AmyRootUser\\disk\\home\\music", ".AmyRootUser\\disk\\home\\pictures",
                     ".AmyRootUser\\disk\\home\\videos"]

    def __init__(self):
        self.install_packages()
        self.create_dirs()

    def create_dirs(self):
        print("VERIFYING DIRECTORIES")
        paths = PackageInstaller.DirsStructure
        for i in paths:
            if not os.path.exists(i):
                # Create the directory if it doesn't exist
                os.makedirs(i)
        print("DIRECTORIES HAS BEEN VERIFIED")

    def install_packages(self):
        print("VERIFYING PACKAGES")
        PipList = PackageInstaller.PipList
        # implement pip as a subprocess:
        for i in PipList:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', i])

        # process output with an API in the subprocess module:
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        print(f'PACKAGES VERYFIED AND INSTALLED \n {installed_packages}')


if __name__ == "__main__":
    pass
