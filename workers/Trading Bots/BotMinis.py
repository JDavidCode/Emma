from glob import glob
from trading import *

volume = 0.20
profit = 1.0
entrys = 0
losses = []


class botCore:
    def __init__(self):
        pass

    def symbolRates(symbol, count, time):
        rates = mt5.copy_rates_from_pos(
            symbol,
            time,
            0,
            count
        )

        rates = pd.DataFrame(rates)
        rates['time'] = pd.to_datetime(rates['time'], unit='s')
        rates['DateTime'] = pd.DatetimeIndex(
            pd.to_datetime(rates['time'], unit='s'))
        rates = rates.set_index('DateTime')
        rsi16 = trading.RSI(rates)

        rates['mm100'] = mm100 = tti.indicators.MovingAverage(
            input_data=rates, period=100).getTiData()
        rates['mm25'] = mm25 = tti.indicators.MovingAverage(
            input_data=rates, period=25).getTiData()
        rates['mm10'] = mm10 = tti.indicators.MovingAverage(
            input_data=rates, period=10).getTiData()
        rates['rsi16'] = rsi16['rsi16']

        return rates

    def signal(symbol):
        rates = botCore.symbolRates(symbol, 450, mt5.TIMEFRAME_M1)
        global backRates
        global entrys
        backRates = rates
        ln = len(rates)-1
        i = 100
        while (i < len(rates)):
            # TO BUY
            if rates['mm100'][i] < rates['mm25'][i] and rates['mm25'][i] < rates['mm10'][i]:
                # and rates['rsi16'][i] > 50.0:
                if rates['rsi16'][i-2] < rates['rsi16'][i] and rates['rsi16'][i] < 80.0:
                    if rates['mm25'][i] < rates['close'][i] or rates['mm25'][i] < rates['open'][i]:
                        if rates['close'][i-1] < rates['open'][i-1]:
                            # print('buy', rates['time'][i])
                            if trading.orderChecker("US100"):
                                trading.orderSender(
                                    "US100", "buy", 0.1, 500, 250)
                            # botCore.backTest(i, 'buy')
                            # entrys += 1
            # TO SELL
            if rates['mm100'][i] > rates['mm25'][i] and rates['mm25'][i] > rates['mm10'][i]:
                # and rates['rsi16'][i] < 50.0:
                if rates['rsi16'][i-2] > rates['rsi16'][i] and rates['rsi16'][i] > 20.0:
                    if rates['mm25'][i] > rates['close'][i] or rates['mm25'][i] > rates['open'][i]:
                        if rates['open'][i-1] > rates['close'][i-1]:
                            # print('Sell', rates['time'][i])
                            if trading.orderChecker("US100"):
                                trading.orderSender(
                                    "US100", "sell", 0.1, 500, 250)

                            # botCore.backTest(i, 'sell')
                            # entrys += 1

            i += 1
        # botCore.showGraphichs(rates, 'M1')

    def showGraphichs(rates, t):
        if t == 'M1':
            fig, axe = plt.subplots(3, 1)
            axe[0].plot(rates['close'], label='Symbol')
            axe[0].plot(rates['mm100'], label='Media Movil 100')
            axe[0].plot(rates['mm10'], label='Media Movil 10')
            axe[0].plot(rates['mm25'], label='Media Movil 25')
            axe[1].plot(rates['rsi16'], color='b')

            plt.plot(rates['rsi16'], label='RSI')
            axe[1].axhline(y=30, color='r', linewidth=1)
            axe[1].axhline(y=50, color='r', linewidth=1)
            axe[1].axhline(y=70, color='r', linewidth=1)
        plt.tight_layout()
        fig.autofmt_xdate()
        plt.show()

    def backTest(point, Atype):
        global backRates
        global profit
        global losses
        opening = backRates['close'][point]
        autoClose = backRates['mm25'][point]
        i = point
        while (i < len(backRates)):

            if Atype == 'buy':
                if backRates['close'][i]-4.9 > opening:
                    profit += 1.0
                    return
                if backRates['close'][i] <= autoClose:
                    profit = profit - 1.0
                    losses.append(
                        (str(backRates['time'][i]), 'buy', backRates['close'][i]))
                    return

            if Atype == 'sell':
                if backRates['close'][i]+4.9 < opening:
                    profit += 1.0
                    return
                if backRates['close'][i] >= autoClose:
                    profit = profit - 1.0
                    losses.append(
                        (str(backRates['time'][i]), 'sell', backRates['close'][i]))
                    return
            i += 1

    def run():
        global losses
        global volume
        global profit
        global entrys
        trading.awake(.10, (0, 0, 0), (100, 5.0), volume)
        botCore.signal("US100")
        print(profit, entrys)
        # print(losses)


if __name__ == '__main__':
    botCore.run()
