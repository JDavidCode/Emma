import importlib
import sys
import os

# from tools.data import toolKit as tools


class toolKit:
    def __init__(self) -> None:
        pass

    def moduleLoader(index):
        json_type = 'dict'
        diccionary = tools.jsonLoader(
            "resources\\json\\module_directory.json", json_type)
        diccionary = diccionary['moduleDirectory']
        key = diccionary.keys()
        try:
            for i in key:
                if index in i:
                    index = diccionary.get(i)
                    print(index)
                    importlib.reload(sys.modules[index])
                    print("module", i, "has been reloaded")
                    importlib.invalidate_caches(sys.modules[index])
        except:
            pass

    def tempClearer():  # TERMINAR######################################
        path = 'c:/Users/Juan/Documents/AmyAssistant/AmyAssistant/.temp'
        os.remove(path)


if __name__ == '__main__':
    toolKit.tempClearer()
