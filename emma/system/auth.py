import os
import emma.config.globals as EMMA_GLOBALS


class Auth:
    def __init__(self):
        self.max_login_attempts = 3

    def authenticate(self):
        for _ in range(self.max_login_attempts):
            option = input("Login, Register, or Invited? ").lower()

            if option == "login":
                if self.login():
                    return
            elif option == "register":
                self.register()
                return
            elif option == "invited":
                self.invited()
                return
            else:
                print("Invalid option. Please try again.")

        print("Too many login attempts. Please try again later.")
        quit()

    def login(self):
        for _ in range(self.max_login_attempts):
            email = input("Email: ")
            password = input("Password: ")

            if email.strip() == "" or password.strip() == "":
                print("Some fields are empty.")
            else:
                if self.perform_login(email, password):
                    return True
                else:
                    print("Incorrect credentials. Please try again.")

        print("Too many login attempts. Please try again later.")
        quit()

    def perform_login(self, email, password):
        x, userData = EMMA_GLOBALS.services_db_lg.user_login(
            email, password)
        if x:
            if userData[0] == "5":
                print("Facial Recognizer is needed for this user level")
                if EMMA_GLOBALS.services_cam_fr.run(userData[2], 1):
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    def register(self):
        # Implement registration logic here
        pass

    def invited(self):
        os.environ["user_lvl"] = "1"
        os.environ["user_name"] = input("insert your name: ")
        os.environ["user_lang"] = input("select your language en/es: ")

    def logout(self):
        # Implement logout logic here
        pass
