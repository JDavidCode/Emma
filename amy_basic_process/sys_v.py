import importlib
import sys
import os
from dotenv import set_key
from tools.data.local.kit import toolKit as localDataTools
from amy_basic_process.data_module import Login
from amy_basic_process.cam_module import FacialRecognizer
import amy_basic_process.miscellaneous as msc


class MainProcess:
    def __init__(self) -> None:
        pass


class BackgroundProcess:
    def __init__(self) -> None:
        pass

    def amyGuardian():
        pass

    def serverShutdown():
        BackgroundProcess.tempClearer()
        BackgroundProcess.envClearer()
        quit()

    def enviroment_clearer():
        clear = [('USERNAME', ''), ('USERLVL', '1'), ('USERLANG', '')]
        for i in clear:
            set_key(".venv/.env", i[0], i[1])

    def temp_clearer():
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

    def module_reloader(index):
        json_type = 'dict'
        diccionary = localDataTools.json_loader(
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

    def global_variables_setter():
        pass


class SystemLogin():
    def __init__(self) -> None:
        pass

    def verify():
        i = 0
        x = input('Login, register or invited?: ')
        if x == 'Login' or x == 'Login':
            return SystemLogin.user_login()
        elif x == 'register' or x == 'Register':
            SystemLogin.userRegister()
        elif x == 'invited' or x == "Invited":
            return Login.invited()
        else:
            print('Incorrect data')
            quit()

    def user_login():
        i = 0
        user = input('Name: ')
        pw = input('Password: ')

        if user == " " or pw == " " or len(user) == 0 or len(pw) == 0:
            print("invalid data")
            i += 1
            if i <= 3:
                SystemLogin.user_login()
            else:
                return

        try:
            x, userData = Login.user_login(user, pw)
            print(x)
            if x:
                if userData[0] == "5":
                    print('Facial Recognizer is needed for this user level')
                    if (FacialRecognizer.run(user, 1) == True):
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                print('incorrect credentials')
                i += 1
                if i <= 3:
                    SystemLogin.user_login()
                else:
                    return
        except:
            print('An error has ocurred on a DB, please contact support')
            if i <= 3:
                SystemLogin.user_login()
            else:
                return

    def user_register():
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
                SystemLogin.userRegister()
            else:
                return
        data = [FacialRecognizer.run(user, 0), ]
        if Login.user_register(user, pw, age, genre, lang, data) == True:
            print('You has been Register')
            print('Now Login Please')
            SystemLogin.user_login()
        else:
            print("ERROR IN REGISTER")


class awake:
    def run():
        userPrefix = Login.user_prefix()
        weather = msc.main.weather('Medellin')
        dateTime = msc.main.date_clock(0)
        dayPart = msc.main.day_parts()
        text = 'good {}, today is {},its {}, {}'.format(
            dayPart, dateTime[1], dateTime[2], weather)
        return userPrefix, text


if __name__ == '__main__':
    pass
