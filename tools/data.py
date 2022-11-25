import json
import re


class toolKit:
    def __init__(self):
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

    def filenameTarget(filename):
        index = ''
        for i in filename:
            if i != '.':
                index += i
            else:
                break
        return index

    def strClearer(index):
        data = index
        if '\'' in index:
            patron = '[\']'
            regex = re.compile(patron)
            data = regex.sub('', index)
        return data

    def listItemRemover(index, list):
        for i in list:
            if i == index:
                list.remove(i)
                return list
            else:
                return list
