from trading_core import *
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

_id = 901
lot = 0.01
daily = (15, 5)
rates = pd.DataFrame


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
        trading(daily)

    def strategy(symbol):
        rates = trading.getSymbolRates(symbol)
        bot.sender('buy', 1.005, 1.002)
        bot.sender('sell', 1.005, 1.002)
        pass

    def sender(type, tp, sl):
        trading.orderSender('EURUSD', type, 0.1, tp, sl, _id)

    def updater():
        pass


if __name__ == "__main__":
    # bot()
    # bot.getDataSet("EURUSD")
    trading(daily)
    dates = trading.getSymbolRates("EURUSD", 5000, mt5.TIMEFRAME_M5)
    bt = Backtest(dates, backtest, commission=.002,
                  exclusive_orders=True, cash=1000, hedging=True)
    stats = bt.run()
    bt.plot()
