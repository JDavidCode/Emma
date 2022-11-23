from trading import *

stock = ['US100Cash']  # 'US30Cash',
balance = 0
pips = 0
vol = 0.0
volRange = {
    150.0: (18.0,  0.1),
    200.0: (21.0, 0.2),
    300.0: (22.0,  0.3),
    500.0: (21.0, 0.5),
    800.0: (22.0,  0.7),
    1000.0: (21.0, 0.9),
    1500.0: (21.0,  1.2),
    2500.0: (21.0, 1.7),
    3500.0: (21.0,  2.2),
    5000.0: (21.0, 2.8),
    10000.0: (21.0,  3.5)
}

keyUs1 = 0
keyUs3 = 0


class botCore:
    def __init__(self) -> None:
        pass

    def volumeRange():
        global balance
        global volRange
        global vol
        global pips
        x = 0.0
        for i in volRange:
            if i < balance:
                x = i
        pips = volRange[x][0]
        vol = volRange[x][1]


if __name__ == '__main__':
    botCore.run()
