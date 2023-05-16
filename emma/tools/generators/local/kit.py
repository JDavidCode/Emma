import datetime
import math
import random
import string
import secrets


class ToolKit:
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

    def print_submultiplos(numero):
        for i in range(1, numero+1):
            if ToolKit.is_multiple_number(numero, i):
                print(f"{i},", end="")

    def is_prime_number(number):
        if number < 2:
            return False
        for i in range(2, int(math.sqrt(number)) + 1):
            if number % i == 0:
                return False
        return True

    def factorial(number):
        if number < 0:
            return None
        if number == 0:
            return 1
        result = 1
        for i in range(1, number + 1):
            result *= i
        return result

    def calculate_hypotenuse(a, b):
        return math.sqrt(a ** 2 + b ** 2)

    def convert_to_binary(number):
        return bin(number)[2:]

    def convert_to_hexadecimal(number):
        return hex(number)[2:]

    def calculate_average(numbers):
        if not numbers:
            return None
        return sum(numbers) / len(numbers)

    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def get_current_date():
        return datetime.date.today()

    def get_current_time():
        return datetime.datetime.now().time()

    def calculate_age(birthdate):
        current_date = datetime.date.today()
        age = current_date.year - birthdate.year
        if current_date.month < birthdate.month or (current_date.month == birthdate.month and current_date.day < birthdate.day):
            age -= 1
        return age

    def is_palindrome(string):
        cleaned_string = ''.join(c.lower() for c in string if c.isalnum())
        return cleaned_string == cleaned_string[::-1]

    def count_vowels(string):
        vowels = 'aeiou'
        count = 0
        for char in string.lower():
            if char in vowels:
                count += 1
        return count

    def calculate_square_root(number):
        if number < 0:
            return None
        return math.sqrt(number)

    def calculate_power(base, exponent):
        return base ** exponent

    def calculate_factorial_recursive(number):
        if number < 0:
            return None
        if number == 0 or number == 1:
            return 1
        return number * ToolKit.calculate_factorial_recursive(number - 1)

    def reverse_string(string):
        return string[::-1]

    def count_words(string):
        words = string.split()
        return len(words)

    def is_perfect_square(number):
        if number < 0:
            return False
        sqrt = math.isqrt(number)
        return sqrt * sqrt == number


if __name__ == "__main__":
    ToolKit.print_submultiplos(600)
