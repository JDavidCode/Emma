import json
import zipfile


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

    def zipper(filename, file):
        with zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as fz:
            fz.write(file)

    def unzipper(filename, path):
        with zipfile.ZipFile(filename, 'r') as zf:
            zf.extractall(
                path=path)

    def toBinary(filename):
        print(filename)
        with open(filename, 'rb') as file:
            binaryDat = file.read()
        return binaryDat

    def fromBinaryToFile(binary, filename):
        with open(filename, 'wb')as file:
            file.write(binary)
