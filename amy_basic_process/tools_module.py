# BasePythonLibraries
import re
import sys
import os
import importlib
import requests
import json
# ImportedPythonLibraries
from bs4 import BeautifulSoup

#################################################################################


class miscellaneousTools:
    def __init__(self) -> None:
        pass

    def strClearer(index):
        data = index
        if '\'' in index:
            patron = '[\']'
            regex = re.compile(patron)
            data = regex.sub('', index)
        return data


class DataTools:
    def __init__(self) -> None:
        pass

    def jsonLoader(index, json_type):
        directory = index
        with open(directory) as f:
            direct = json.load(f)
            for i in direct:
                if json_type == 'list':
                    diccionary = []
                    diccionary = direct[i].copy()
                    return diccionary
                elif json_type == 'dict':
                    diccionary = {}
                    diccionary = direct[0].copy()
                    return diccionary

    def csvGenerator():  # PARA TERMINAR
        entity = list()
        url = input('Ingrese la URL: ')
        itemType = input('Ingrese el tipo de elemento: ')
        itemClass = input('Ingrese la clase: ')
        request = requests.get(url)
        page = BeautifulSoup(request.content, 'html.parser')
        item = page.find_all(itemType, class_=itemClass)

        for i in item:
            entity.append(i.text)


class rootTools:
    def __init__(self) -> None:
        pass

    def moduleLoader(index):
        json_type = 'dict'
        diccionary = DataTools.jsonLoader(
            "resources\\json\\module_directory.json", json_type)
        diccionary = diccionary['moduleDirectory']
        key = diccionary.keys()
        try:
            for i in key:
                if index in i:
                    index = diccionary.get(i)
                    importlib.reload(sys.modules[index])
        except:
            pass


if __name__ == '__main__':
    DataTools.jsonUpdater()
