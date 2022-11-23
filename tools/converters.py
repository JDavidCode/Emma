from PIL import Image
import zipfile
import os
import tools.data as data


class ToolKit:
    def __init__(self) -> None:
        pass

    def imageConverter(openURL):
        filename = data.toolKit.filenameTarget(openURL)
        img = Image.open(openURL)
        #rgb_img = img.convert('RGB')
        img.save(filename, 'png')

    def zipper(filename, file):
        with zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as fz:
            fz.write(file, arcname=os.path.basename(file))

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


if __name__ == '__main__':
    pass
