import random
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

    def random_number_list(leng=None, rang=None):
        randomlist = []
        if leng == None:
            leng = random.randint(5, 50)
        if rang == None:
            rang = random.randint(10, 100)
        for i in range(0, leng):
            n = random.randint(1, rang)
            randomlist.append(n)
        return randomlist

    def random_hex_color():
        # Generating a random number in between 0 and 2^24
        color = random.randrange(0, 2**24)
        # Converting that number from base-10 (decimal) to base-16 (hexadecimal)
        hex_color = hex(color)
        std_color = "#" + hex_color[2:]

        return std_color

    def random_rgb_color():
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        rgb = [r, g, b]
        return rgb

    def random_number(rang=None):
        if rang == None:
            rang = 100

        return random.randint(0, rang)

    def random_even_number(rang=None):
        if rang == None:
            rang = 100

        for x in range(0, rang):
            r = random.randint(0, rang)
            if r % 2 == 0:
                return r

    def random_odd_number(rang=None):
        if rang == None:
            rang = 100

        for x in range(0, rang):
            r = random.randint(0, rang)
            if r % 2 != 0:
                return r

    def is_multiple_number(numero, multiplo):
        return numero % multiplo == 0

    def imprimir_submultiplos(numero):
        for i in range(1, numero+1):
            if toolkit.es_multiplo(numero, i):
                print(f"{i},", end="")


if __name__ == "__main__":
    toolkit.imprimir_submultiplos(25920)
