from amy_basic_process.data_module import login
from amy_basic_process.cam_module import facialRecognizer


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
            return systemLogin.invited()
        else:
            print('Incorrect data')
            if i < 3:
                systemLogin.verify()
                i += 1
            else:
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

    def invited():
        return login.invited()


if __name__ == '__main__':
    systemLogin.verify()
