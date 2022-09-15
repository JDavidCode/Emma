from amy_basic_process.data_module import login
from amy_basic_process.cam_module import facialRecognizer


class systemLogin():
    def __init__(self) -> None:
        pass

    def verify():
        x = input('login or register?: ')
        if x == 'login' or x == 'Login':
            return systemLogin.userLogin()
        elif x == 'register' or x == 'Register':
            systemLogin.userRegister()
        else:
            print('Incorrect data')
            systemLogin.verify()

    def userLogin():
        user = input('Name: ')
        pw = input('Password: ')
        x, userData = login.userLogin(user, pw)
        if x == True:
            print(userData[1:])
            if facialRecognizer.run(user, 1) == True:
                return True
            else:
                return False
        else:
            print('incorrect credentials')
            return False

    def userRegister():
        user = input('Name: ')
        pw = input('Password: ')
        age = int(input('Age: '))
        genre = input('genre (Male/Female): ')
        faceRut = facialRecognizer.run(user, 0)
        if login.userRegister(user, pw, age, genre, faceRut) == True:
            print('You has been Register')
            print('Now Login Please')
            systemLogin.userLogin()
        elif login.userRegister(user, pw, age, genre) == False:
            systemLogin.userRegister()


if __name__ == '__main__':
    systemLogin.verify()
