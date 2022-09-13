from amy_basic_process.data_module import login


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
            print(userData)
            return True
        else:
            print('incorrect credentials')
            return

    def userRegister():
        user = input('Name: ')
        pw = input('Password: ')
        age = input('Age: ')
        genre = input('genre (Male/Female): ')
        if login.userRegister(user, pw, age, genre) == True:
            print('You has been Register')
            print('Now Login Please')
            systemLogin.userLogin()
        elif login.userRegister(user, pw, age, genre) == False:
            systemLogin.userRegister()
