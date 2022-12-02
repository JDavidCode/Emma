import datetime
import requests
import time


class main:
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

    def dateClock(type):
        dateTime = datetime.datetime.now()
        clock = dateTime.time()
        date = dateTime.date()

        if type == 1:
            return dateTime.strftime('%d-%m of %Y %H:%M:%S')
        elif type == 2:
            return date
        elif type == 3:
            return clock.strftime('%H:%M:%S')
        else:
            return dateTime.strftime('%d-%m of %Y %H:%M:%S'), date, clock.strftime('%H:%M:%S')

    def dayParts():
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


class geoLoc:
    def __init__(self) -> None:
        pass


class directories:
    def __init__(self) -> None:
        pass

    def localDirectories():
        pass

    def userDirectories():
        pass


if __name__ == '__main__':
    print(main.weather('medellin'))
