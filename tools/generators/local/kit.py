import string
import secrets


class toolkit:
    def __init__(self) -> None:
        pass

    def password_generator(lenght):
        pw = ''
        i = 0
        chars = string.ascii_letters
        numbers = string.digits
        symbols = string.punctuation
        setter = chars + numbers + symbols
        for i in range(lenght):
            pw += ''.join(secrets.choice(setter))
        return pw
