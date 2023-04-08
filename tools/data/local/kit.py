import json
import re


class toolKit:
    def __init__(self):
        pass

    def json_loader(index, json_type, i):
        directory = index
        with open(directory) as f:
            direct = json.load(f)
            if json_type == 'list':
                diccionary = []
                diccionary = direct[i].copy()
                return diccionary
            elif json_type == 'dict':
                diccionary = {}
                diccionary = direct[i].copy()
                return diccionary

    def filename_target(filename):
        index = ''
        for i in filename:
            if i != '.':
                index += i
            else:
                break
        return index

    def format_target(filename, pandoc):
        json = 0
        if (pandoc):
            json = toolKit.jsonLoader(
                "assets\\json\\extensions.json", "list", "PANDOC_FORMATS")
        else:
            json = toolKit.jsonLoader(
                "assets\\json\\extensions.json", "dict", "FORMATS")
        for i in json:
            if filename.endswith(f".{i}"):
                return i
        print("The target has not format, is not supported or is unrecognized")
        return 0

    def string_symbol_clearer(index):
        if '\'' in index:
            patron = '[\']'
            regex = re.compile(patron)
            index = regex.sub('', index)
        return index

    def string_voids_clearer(index):
        rev = 0
        for i in index:
            if i == ' ':
                rev += 1
            else:
                break
        return index[rev:]

    def item_list_remover(index, list):
        for i in list:
            if i == index:
                list.remove(i)
                return list
            else:
                return list


if __name__ == "__main__":
    pass
