import re
import requests
import time


class ToolKit:
    def __init__(self):
        pass

    def strClearer(index):
        data = index
        if '\'' in index:
            patron = '[\']'
            regex = re.compile(patron)
            data = regex.sub('', index)
        return data

    def weather(city):
        url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=163ea3a6fc8b3ea62e3f640d2b53567b'.format(
            city)
        quest = requests.get(url)
        data = quest.json()
        temperature = data['main']['temp']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        wind_Speed = data['wind']['speed']
        description = data['weather'][0]['description']

        print("Clima en ", city, "\n", "Temperatura:", temperature, "\n", "Temperatura minima:", temp_min,
              "\n", "Temperatura Maxima:", temp_max, "\n", "Velocidad del viento:", wind_Speed, "\n", "Descripcion:", description)

        return

    def time():
        x = time.time()
        x = time.localtime(x)
        year = x[0]
        yday = x[7]
        month = x[1]
        day = x[2]
        hour = x[3]
        minute = x[4]
        sec = x[5]

        calendar = time.strftime("%A %d %B of %Y", x)
        local_t = time.strftime("%I : %M : %S, %p", x)
        print(calendar, "\n", local_t)

        return


if __name__ == '__main__':
    pass
