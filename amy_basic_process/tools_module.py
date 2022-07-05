# BasePythonLibraries
import re
import sys
import importlib
import requests
from threading import Thread
# ImportedPythonLibraries
from bs4 import BeautifulSoup

modulesDiccionary = {
    'data': 'amy_basic_process.data_module',
    'voice': 'amy_basic_process.voice_module',
    'tools': 'amy_basic_process.tools_module',
    'task': 'amy_basic_process.task_module'
}

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
        key = modulesDiccionary.keys()
        try:
            for i in key:
                if index in i:
                    index = modulesDiccionary.get(i)
                    importlib.reload(sys.modules[index])
        except:
            pass


if __name__ == '__main__':
    pass
