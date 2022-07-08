import re


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
