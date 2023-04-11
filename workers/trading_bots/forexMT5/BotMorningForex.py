from trading_core import *
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np
_id = 901
lot = 0.01
daily = (15, 5)
rates = pd.DataFrame
pair = "BTCUSD"


class backtest(Strategy):
    def __init__(self):
        pass


class bot:
    def __init__(self):
        tradingMT5(daily)
        bot.strategy("EURUSD")

    def strategy(symbol):
        rates = mt5.get_symbol_rates(symbol)

        pass

    def sender(type, tp, sl):
        pass

    def updater():
        pass


if __name__ == "__main__":
    pass
