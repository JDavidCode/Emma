import os
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from tools.data import toolKit as tools

v = -15


class toolKit:
    def __init__(self):
        pass

    def volume(index):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volumeRange = volume.GetVolumeRange()

        global v

        if index == 'up':
            v += 5
            volume.SetMasterVolumeLevel(v, None)
        elif index == 'down':
            v -= 5
            volume.SetMasterVolumeLevel(v, None)
        else:
            pass

    def pathMover():
        json_type = 'dict'
        diccionary = tools.jsonLoader(
            "resources\\json\\path_directory.json", json_type)
        downFolder = diccionary.get('downloads')
        for filename in os.listdir(downFolder):
            name, extension = os.path.splitext(downFolder + filename)

            if extension in ['.jpg', '.jpeg', '.png']:
                folder = diccionary.get('pictures')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')

            if extension in ['.mov', '.mkv', '.mp4', '.wmv', '.flv']:
                folder = diccionary.get('videos')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')

            if extension in ['.wav', '.wave', '.bwf', '.aac', '.m4a', '.mp3']:
                folder = diccionary.get('music')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')

            if extension in ['.txt', '.docx', '.doc', '.pptx', '.ppt', 'xls', '.xlsx']:
                folder = diccionary.get('documents')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')


if __name__ == '__main__':
    pass
