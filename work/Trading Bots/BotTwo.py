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
        rlen = len(rates)-2
        type = ''
        if rates['mm5'][rlen] > rates['mm12'][rlen] and rates['mm'][rlen] > rates['mm5'][rlen] and rates['close'][rlen] > rates['mm5'][rlen]:
            backward = float(
                round(rates['high'][rlen], 5) - round(rates['close'][rlen], 5))
            # print(symbol, 'MM PASS')
            if rates['mmt12'][rlen] < 100.15 and rates['mmt12'][rlen-1] < rates['mmt12'][rlen] and backward < 0.00020:
                # print(symbol, 'mmt12 and backward PASS')
                type = 'buy'
                return type
        if rates['mm12'][rlen] > rates['mm5'][rlen] and rates['mm5'][rlen] > rates['mm'][rlen] and rates['mm5'][rlen] > rates['close'][rlen]:
            backward = float(
                round(rates['close'][rlen], 5) - round(rates['low'][rlen], 5))
            # print(symbol, 'MM PASS')
            if rates['mmt12'][rlen] > 99.85 and rates['mmt12'][rlen] > rates['mmt12'][rlen-1] and backward < 0.00020:
                # print(symbol, 'mmt12 and backward PASS')
                type = 'sell'
                return type
        return type

    def signal_1H(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_H1)
        rlen = len(rates)-2
        type = ''

        if rates['open'][rlen] > rates['mm12'][rlen] and rates['close'][rlen] > rates['mm12'][rlen] and rates['mm'][rlen] > rates['mm12'][rlen] and rates['cci10'][rlen] > 0 and rates['cci10'][rlen] < 125:
            backward = float(
                round(rates['high'][rlen], 5) - round(rates['close'][rlen], 5))
            if rates['mmt12'][rlen-1] < rates['mmt12'][rlen] and rates['mmt12'][rlen] > 100.0 and rates['mmt12'][rlen] < 100.20 and backward < 0.0007:
                type = 'buy'
                return type
        elif rates['open'][rlen] < rates['mm12'][rlen] and rates['close'][rlen] < rates['mm12'][rlen] and rates['mm'][rlen] > rates['mm12'][rlen] and rates['cci10'][rlen] < 0 and rates['cci10'][rlen] > -125:
            backward = float(
                round(rates['close'][rlen], 5) - round(rates['low'][rlen], 5))
            if rates['mmt12'][rlen-1] > rates['mmt12'][rlen] and rates['mmt12'][rlen] < 100.0 and rates['mmt12'][rlen] > 99.80 and backward < 0.0007:
                type = 'sell'
                return type
        return type

    def run():
        trading.awake()
        global volume
        for i in stock:
            if trading.timeSchedule() and trading.win_loss_Stopper():
                if trading.spread(i) and trading.orderChecker(i):
                    t = trading.signal_1H(i)
                    b = trading.entryBreak(i, 5.0, 0.0)
                    if b == True:
                        trading.orderSender(
                            i, t, volume, 0.0055, 0.002, 2)
                    else:
                        pass
                if trading.spread(i) and trading.orderChecker(i):
                    t = trading.signal_15M(i)
                    b = trading.entryBreak(i, 1.0, 15.0)
                    if b == True:
                        trading.orderSender(
                            i, t, volume, 0.0025, 0.001, 1)
                    else:
                        pass
            # trading.orderUpdater(i)
            # trading.orderCloser()
        time.sleep(0.3)


if __name__ == '__main__':
    pass
