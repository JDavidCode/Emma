import json
import re


class toolKit:
    def __init__(self):
        pass

    def json_loader(path, i, json_type="dict"):
        with open(path) as f:
            direct = json.load(f)
            if json_type == 'list':
                dictionary = direct.get(i, [])
            elif json_type == 'dict':
                dictionary = direct.get(i, {})
            elif json_type == 'command':
                dictionary = direct.get(i, None)
            return dictionary

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
                "assets\\json\\extensions.json", "PANDOC_FORMATS", "list")
        else:
            json = toolKit.jsonLoader(
                "assets\\json\\extensions.json", "FORMATS", "dict")
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
