from PIL import Image
import zipfile
import os
from tools.data.local.kit import toolKit as localDataTools


class toolKit:
    def __init__(self) -> None:
        pass

    def imageConverter(openURL):
        filename = localDataTools.filenameTarget(openURL)
        img = Image.open(openURL)
        #rgb_img = img.convert('RGB')
        img.save(filename, 'png')

    def zipper(path):
        for i in path:
            with zipfile.ZipFile(i[1], 'w', compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=9) as fz:
                fz.write(i[0], arcname=os.path.basename(i[0]))

    def unzipper(path):
        for i in path:
            with zipfile.ZipFile(i[0], 'r') as fz:
                fz.extractall(path=i[1])

    def toBinary(filename):
        print(filename)
        with open(filename, 'rb') as file:
            binaryDat = file.read()
        return binaryDat

    def fromBinaryToFile(binary, filename):
        with open(filename, 'wb')as file:
            file.write(binary)


if __name__ == "__main__":
    pass
