# BasePythonLibraries
import os
# ImportedPythonLibraries
from tools.data import toolKit as tools

#################################################################################


class webModule:
    def __init__(self):
        pass


class osModule:
    def __init__(self):
        pass

    def openApp(index):
        json_type = 'dict'
        diccionary = tools.jsonLoader(
            "res\\json\\osApp_directory.json", json_type)
        diccionary = diccionary['appDirectory']
        keys = diccionary.keys()
        if index in keys:
            get = diccionary.get(index)
            os.startfile(get)

    def pathMover():
        json_type = 'dict'
        diccionary = tools.jsonLoader(
            "res\\json\\path_directory.json", json_type)
        downFolder = diccionary.get('downloads')
        for filename in os.listdir(downFolder):
            name, extension = os.path.splitext(downFolder + filename)

            if extension in ['.jpg', '.jpeg', '.png']:
                folder = diccionary.get('pictures')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')

            if extension in ['.mov', '.mkv', '.mp4', '.wmv', '.flv']:
                folder = diccionary.get('videos')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')

            if extension in ['.wav', '.wave', '.bwf', '.aac', '.m4a', '.mp3']:
                folder = diccionary.get('music')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')

            if extension in ['.txt', '.docx', '.doc', '.pptx', '.ppt', 'xls', '.xlsx']:
                folder = diccionary.get('documents')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('changes have been applied')


class mathModule:
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
