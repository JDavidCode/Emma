import requests
from bs4 import BeautifulSoup


class web:
    def __init__(self):
        pass

    def csvGenerator():  # PARA TERMINAR
        entity = list()
        url = input('set a URL: ')
        item_Type = input('set a element type: ')
        item_Class = input('set a element class: ')
        request = requests.get(url)
        page = BeautifulSoup(request.content, 'html.parser')
        item = page.find_all(item_Type, class_=item_Class)

        for i in item:
            entity.append(i.text)
