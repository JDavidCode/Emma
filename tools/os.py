from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from tools.data import toolKit as tools


class toolKit:
    def __init__(self):
        pass

    def volume(index):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume_Range = volume.GetVolumeRange()
        v = volume.GetChannelVolumeLevel(1)

        if index == 'up':
            v += 5
            volume.SetMasterVolumeLevel(v, None)
        elif index == 'down':
            v -= 5
            volume.SetMasterVolumeLevel(v, None)
        else:
            pass


if __name__ == '__main__':
    pass
