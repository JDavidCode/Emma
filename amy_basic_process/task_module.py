# BasePythonLibraries
import os
# ImportedPythonLibraries
import pywhatkit as PWK
import wikipedia as WK
import amy_basic_process.tools_module as tools

#################################################################################

wLanguaje = WK.set_lang('en')


class webModule:
    def __init__(self):
        pass

    def YTPlayer(index):
        PWK.playonyt(index)
        return 0

    def WhatIS(index):
        wiki = WK.summary(index, 1)
        return wiki


class osModule:
    def __init__(self):
        pass

    def pathMover():
        json_type = 'dict'
        diccionary = tools.DataTools.jsonLoader(
            "resources\\json\\path_directory.json", json_type)
        downFolder = diccionary.get('downloads')
        for filename in os.listdir(downFolder):
            name, extension = os.path.splitext(downFolder + filename)

            if extension in ['.jpg', '.jpeg', '.png']:
                folder = diccionary.get('pictures')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('cambio realizado con exito')

            if extension in ['.mov', '.mkv', '.mp4', '.wmv', '.flv']:
                folder = diccionary.get('videos')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('cambio realizado con exito')

            if extension in ['.wav', '.wave', '.bwf', '.aac', '.m4a', '.mp3']:
                folder = diccionary.get('music')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('cambio realizado con exito')

            if extension in ['.txt', '.docx', '.doc', '.pptx', '.ppt', 'xls', '.xlsx']:
                folder = diccionary.get('documents')
                os.rename(downFolder + '\\' + filename,
                          folder + '\\' + filename)
                print('cambio realizado con exito')

    def OpenApp(index):
        json_type = 'dict'
        diccionary = tools.DataTools.jsonLoader(
            "resources\\json\\osApp_directory.json", json_type)
        diccionary = diccionary['appDirectory']
        keys = diccionary.keys()
        if index in keys:
            get = diccionary.get(index)
            os.startfile(get)


class mathModule:
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
