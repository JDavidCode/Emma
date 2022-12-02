from random import randint
import secrets
import string
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

    def scrapper():
        pass


class locale:
    def __init__(self) -> None:
        pass

    def passwordGenerator(l):
        pw = ''
        i = 0
        chars = string.ascii_letters
        numbers = string.digits
        symbols = string.punctuation
        setter = chars + numbers + symbols
        for i in range(l):
            pw += ''.join(secrets.choice(setter))
        return pw


if __name__ == "__main__":
    pass
