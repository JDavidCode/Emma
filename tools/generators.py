import requests
from bs4 import BeautifulSoup


class web:
    def __init__(self):
        pass

    def csvGenerator():  # PARA TERMINAR
        entity = list()
        url = input('set a URL: ')
        itemType = input('set a element type: ')
        itemClass = input('set a element class: ')
        request = requests.get(url)
        page = BeautifulSoup(request.content, 'html.parser')
        item = page.find_all(itemType, class_=itemClass)

        for i in item:
            entity.append(i.text)
