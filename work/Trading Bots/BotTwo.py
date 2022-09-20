from trading import *

volume = 0.03

stock = ['EURUSD', 'EURNZD', 'EURAUD', 'EURCHF',
         'EURCAD', 'EURGBP', 'EURSGD', 'GBPCHF', 'GBPCAD',
         'GBPAUD', 'GBPNZD', 'GBPUSD', 'AUDUSD',
         'AUDNZD', 'AUDCHF', 'AUDCAD', 'NZDCAD',
         'NZDCHF', 'NZDUSD', 'USDCAD', 'USDCHF']


class botCore:
    def __init__(self) -> None:
        pass

    def signal_15M(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_M30)
        l = len(rates)-2
        type = ''
        if rates['mm5'][l] > rates['mm12'][l] and rates['mm'][l] > rates['mm5'][l] and rates['close'][l] > rates['mm5'][l]:
            backward = float(
                round(rates['high'][l], 5) - round(rates['close'][l], 5))
            # print(symbol, 'MM PASS')
            if rates['mmt12'][l] < 100.15 and rates['mmt12'][l-1] < rates['mmt12'][l] and backward < 0.00020:
                # print(symbol, 'mmt12 and backward PASS')
                type = 'buy'
                return type
        if rates['mm12'][l] > rates['mm5'][l] and rates['mm5'][l] > rates['mm'][l] and rates['mm5'][l] > rates['close'][l]:
            backward = float(
                round(rates['close'][l], 5) - round(rates['low'][l], 5))
            # print(symbol, 'MM PASS')
            if rates['mmt12'][l] > 99.85 and rates['mmt12'][l] > rates['mmt12'][l-1] and backward < 0.00020:
                # print(symbol, 'mmt12 and backward PASS')
                type = 'sell'
                return type
        return type

    def signal_1H(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_H1)
        l = len(rates)-2
        type = ''

        if rates['open'][l] > rates['mm12'][l] and rates['close'][l] > rates['mm12'][l] and rates['mm'][l] > rates['mm12'][l] and rates['cci10'][l] > 0 and rates['cci10'][l] < 125:
            backward = float(
                round(rates['high'][l], 5) - round(rates['close'][l], 5))
            if rates['mmt12'][l-1] < rates['mmt12'][l] and rates['mmt12'][l] > 100.0 and rates['mmt12'][l] < 100.20 and backward < 0.0007:
                type = 'buy'
                return type
        elif rates['open'][l] < rates['mm12'][l] and rates['close'][l] < rates['mm12'][l] and rates['mm'][l] > rates['mm12'][l] and rates['cci10'][l] < 0 and rates['cci10'][l] > -125:
            backward = float(
                round(rates['close'][l], 5) - round(rates['low'][l], 5))
            if rates['mmt12'][l-1] > rates['mmt12'][l] and rates['mmt12'][l] < 100.0 and rates['mmt12'][l] > 99.80 and backward < 0.0007:
                type = 'sell'
                return type
        return type

    def run():
        global volume
        trading.awake(0.0003, (0.00150, 0.0003, 0.0006), (30.0, 15.0), volume)
        while True:
            for i in stock:
                if trading.timeSchedule() and trading.win_loss_Stopper():
                    if trading.spread(i) and trading.orderChecker(i):
                        t = botCore.signal_1H(i)
                        b = trading.entryBreak(i, 5.0, 0.0)
                        if b == True:
                            trading.orderSender(
                                i, t, volume, 0.0055, 0.002)
                        else:
                            pass
                    if trading.spread(i) and trading.orderChecker(i):
                        t = botCore.signal_15M(i)
                        b = trading.entryBreak(i, 1.0, 15.0)
                        if b == True:
                            trading.orderSender(
                                i, t, volume, 0.0025, 0.001)
                        else:
                            pass
                # trading.orderUpdater(i)
                # trading.orderCloser()
            time.sleep(0.3)


if __name__ == '__main__':
    botCore.run()
