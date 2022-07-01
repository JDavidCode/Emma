# BasePythonLibraries
import re
import time
from threading import Thread
# ImportedPythonLibraries
#################################################################################
# AppLibraries

#################################################################################
#################################################################################

taskIndexer = ['play on', 'read about', 'open']


class DataTool:
    def __init__(self) -> None:
        pass

    def taskIndexer(index):
        index = index
        respaldo = index
        charts = ''
        for i in taskIndexer:
            if i in index:
                index = i
                respaldo = respaldo.replace(i, '')
                charts = len(respaldo)
                respaldo = respaldo[1:charts]
                print(respaldo)
                print(index)
        return index, respaldo

    def strClearer(index):
        data = index
        if '\'' in index:
            patron = '[\']'
            regex = re.compile(patron)
            data = regex.sub('', index)
        return data

# Leer cada dato de la lista taskIndex y verificar


if __name__ == '__main__':
    pass
