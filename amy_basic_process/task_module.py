# BasePythonLibraries
import os
import datetime
import requests
import time
import pywhatkit
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import webbrowser
# ImportedPythonLibraries
from tools.data.local.kit import toolKit as localDataTools
#################################################################################


class WebModule:
    def __init__(self):
        pass

    def youtube_player(index):
        pywhatkit.playonyt(index)

    def google_search(index):
        pywhatkit.search(index)

    def open_website(index):
        json = localDataTools.json_loader(
            "assets\\json\\web_sites.json", "web_dir", 'dict')
        for i in json.keys():
            if i == index:
                get = json.get(i)
                webbrowser.open(get)

    def open_local_site():
        webbrowser.open("http://192.168.1.3:3018/")


class OsModule:
    def __init__(self):
        pass

    def open_app(index):
        json = localDataTools.json_loader(
            "assets\\json\\app_directory.json", "app_dir", 'dict')
        for i in json.keys():
            if i == index:
                get = json.get(i)
                os.startfile(get)

    def path_mover():
        diccionary = localDataTools.json_loader(
            "assets\\json\\path_directory.json", 'amy_paths', 'dict')
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

    def volume_management(index):
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
        elif index == 'mute':
            v -= 50
            volume.SetMasterVolumeLevel(v, None)
        else:
            pass


class MiscellaneousModule:
    def __init__(self):
        pass

    def weather(city):
        url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=163ea3a6fc8b3ea62e3f640d2b53567b'.format(
            city)
        quest = requests.get(url)
        data = quest.json()
        temperature = int(data['main']['temp'])
        temp_min = int(data['main']['temp_min'])
        temp_max = int(data['main']['temp_max'])
        wind_Speed = int(data['wind']['speed'])
        description = data['weather'][0]['description']

        wt = "This is the weather in {}, current temperature {} °, minimum temperature {} °, maximum temperature {} °, wind speed {} meters per second".format(
            city, temperature, temp_min, temp_max, wind_Speed)

        return wt

    def date_clock(i):
        dateTime = datetime.datetime.now()
        clock = dateTime.time()
        date = dateTime.date()

        if i == 1:
            return dateTime.strftime('%d-%m %Y %H:%M:%S')
        elif i == 2:
            return date
        elif i == 3:
            return clock.strftime('%H:%M:%S')
        else:
            return dateTime.strftime('%d-%m  %Y %H:%M:%S'), date, clock.strftime('%H:%M:%S')

    def day_parts():
        t = datetime.datetime.today()
        nDate = datetime.date.today()
        timeSchedule = ['{} 5:00:00'.format(
            nDate), '{} 12:00:00'.format(nDate), '{} 17:00:00'.format(nDate), '{} 21:00:00'.format(nDate)]

        morning = time.strptime(timeSchedule[0], '%Y-%m-%d %H:%M:%S')
        morning = datetime.datetime.fromtimestamp(time.mktime(morning))
        afternoon = time.strptime(timeSchedule[1], '%Y-%m-%d %H:%M:%S')
        afternoon = datetime.datetime.fromtimestamp(time.mktime(afternoon))
        evening = time.strptime(timeSchedule[2], '%Y-%m-%d %H:%M:%S')
        evening = datetime.datetime.fromtimestamp(time.mktime(evening))
        night = time.strptime(timeSchedule[3], '%Y-%m-%d %H:%M:%S')
        night = datetime.datetime.fromtimestamp(time.mktime(night))

        if t > morning and t < afternoon:
            return 'morning'
        elif t > afternoon and t < evening:
            return 'afternoon'
        elif t > evening and t < night:
            return 'evening'
        else:
            return 'night'

    class GeoLocation:
        def __init__(self) -> None:
            pass


class MathModule:
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
