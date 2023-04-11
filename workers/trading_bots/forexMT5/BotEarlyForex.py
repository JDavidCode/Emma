from trading_core import *

_id = 901
lot = 0.01
daily = (15, 5)
rates = pd.DataFrame
pair = "BTCUSD"


class backtest(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(ti.SMA, price, 15)
        self.ma2 = self.I(ti.SMA, price, 30)
        self.ma3 = self.I(ti.SMA, price, 80)

    def next(self):
        if crossover(self.ma1, self.ma2):
            if crossover(self.ma2, self.ma3):
                self.buy()
        elif crossover(self.ma2, self.ma1):
            if crossover(self.ma3, self.ma2):
                self.sell()


class bot():
    def __init__(self):
        tradingMT5(daily)
        bot.strategy("EURUSD")

    def strategy(symbol):
        while True:
            ohlcv = mt5.copy_rates_from(
                symbol, mt5.TIMEFRAME_M1, 1000)
            close = np.array([x.close for x in ohlcv])
            # calculate RSI, CCI, and Bollinger Bands
            rsi = ti.RSI(close, timeperiod=12)
            cci = ti.CCI(ohlcv[:, 1], ohlcv[:, 2], ohlcv[:, 3], timeperiod=16)
            upper, middle, lower = ti.BBANDS(close, timeperiod=18)

            buy_signal = (rsi < 30) & (cci < -100) & (close < lower)
            sell_signal = (rsi > 70) & (cci > 100) & (close > upper)
            # print the signals
            if buy_signal.any():
                print("Buy signal detected.")
            if sell_signal.any():
                print("Sell signal detected.")

            time.sleep(75)

    def sender(type, tp, sl):
        tradingMT5.order_sender('EURUSD', type, 0.1, tp, sl, _id)

    def updater():
        pass


if __name__ == "__main__":
    # bot()
    # bot.getDataSet("EURUSD")
    bot()
