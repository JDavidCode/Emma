import sys
import subprocess

PipList = ["Backtesting", "MetaTrader5",
           "assets\\TA_Lib-0.4.24-cp310-cp310-win_amd64.whl", "pyfredapi"]


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
