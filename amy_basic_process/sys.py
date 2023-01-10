import importlib
import sys
import os
from dotenv import set_key
from tools.data.local.kit import toolKit as localDataTools
from amy_basic_process.data_module import login
from amy_basic_process.cam_module import facialRecognizer


class mainProcess:
    def __init__(self) -> None:
        pass


class backgroundProcess:
    def __init__(self) -> None:
        pass

    def amyGuardian():
        pass

    def serverShutdown():
        backgroundProcess.tempClearer()
        backgroundProcess.envClearer()
        quit()

    def envClearer():
        clear = [('USERNAME', ''), ('USERLVL', '1'), ('USERLANG', '')]
        for i in clear:
            set_key(".venv/.env", i[0], i[1])

    def tempClearer():
        path = '.temp'
        for file in os.listdir(path):
            x = path+'\\'+file
            try:
                os.rmdir(x)
            except:
                pass
            try:
                os.remove(x)
            except:
                pass

    def moduleReloader(index):
        json_type = 'dict'
        diccionary = localDataTools.jsonLoader(
            "assets\\json\\module_directory.json", json_type)
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

    def globalVariableSetter():
        pass


class systemLogin():
    def __init__(self) -> None:
        pass

    def verify():
        i = 0
        x = input('login, register or invited?: ')
        if x == 'login' or x == 'Login':
            return systemLogin.userLogin()
        elif x == 'register' or x == 'Register':
            systemLogin.userRegister()
        elif x == 'invited' or x == "Invited":
            return login.invited()
        else:
            print('Incorrect data')
            quit()

    def userLogin():
        i = 0
        user = input('Name: ')
        pw = input('Password: ')

        if user == " " or pw == " " or len(user) == 0 or len(pw) == 0:
            print("invalid data")
            i += 1
            if i <= 3:
                systemLogin.userLogin()
            else:
                return

        try:
            x, userData = login.userLogin(user, pw)
            if x:
                if userData[1] == "5":
                    print('Facial Recognizer is needed for this user level')
                    if (facialRecognizer.run(user, 1) == True):
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                print('incorrect credentials')
                i += 1
                if i <= 3:
                    systemLogin.userLogin()
                else:
                    return
        except:
            print('incorrect credentials')
            if i <= 3:
                systemLogin.userLogin()
            else:
                return

    def userRegister():
        i = 0
        user = input('Name: ')
        pw = input('Password: ')
        age = int(input('Age: '))
        lang = input('Lang (es/en): ')
        genre = input('genre (Male/Female): ')
        if user == " " or pw == " " or age == " " or genre == " " or len(user) == 0 or len(pw) == 0 or len(str(lang)) == 0 or len(genre) == 0:
            i += 1
            print("invalid data")
            if i <= 3:
                systemLogin.userRegister()
            else:
                return
        data = [facialRecognizer.run(user, 0), ]
        if login.userRegister(user, pw, age, genre, lang, data) == True:
            print('You has been Register')
            print('Now Login Please')
            systemLogin.userLogin()
        else:
            print("ERROR IN REGISTER")


if __name__ == '__main__':
    mainProcess.tempClearer()
