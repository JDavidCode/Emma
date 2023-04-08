from trading_core import tradingIqOption, ti, time, np


class bot:
    def __init__(self, iq_option):
        print("MRSIC (DOUBLE MA, RSI & CCI) IS OPERATING")
        self.iq = iq_option
        bot.strategy(self)

    def strategy(self):
        asset_id = "EURUSD"
        timeWait = 60
        onLoose = False

        rates = self.iq.get_symbol_rates(asset_id)

        # Calculate RSI and CCI indicators
        rsi = ti.RSI(rates["Close"], timeperiod=14)
        cci = ti.CCI(rates["High"], rates["Low"],
                     rates["Close"], timeperiod=20)

        # Calculate Moving Averages
        short_ma = rates["Close"].rolling(window=5).mean()
        long_ma = rates["Close"].rolling(window=20).mean()
        # Check conditions and make a trade decision
        last_rsi = rsi[-1]
        last_cci = cci[-1]
        last_close = rates["Close"][-1]
        last_short_ma = short_ma[-1]
        last_long_ma = long_ma[-1]

        if last_close > last_short_ma and last_close > last_long_ma and last_rsi < 30 and last_cci < -100:
            # Place a call option
            if (self.iq.loss_stopper() or onLoose):
                onLoose = False
                timeWait = 60
                self.iq.order_sender(asset_id, "call", 1, 100)
            else:
                onLoose = True
                timeWait = 135
        elif last_close < last_short_ma and last_close < last_long_ma and last_rsi > 70 and last_cci > 100:
            # Place a put option
            if (self.iq.loss_stopper() or onLoose):
                onLoose = False
                timeWait = 60
                self.iq.order_sender(asset_id, "put", 1, 100)
            else:
                onLoose = True
                timeWait = 135
        # Wait 1 minute before checking the indicators again
        time.sleep(timeWait)


if __name__ == "__main__":
    pass
