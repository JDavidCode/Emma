from trading_core import tradingIqOption, ti, time, np


class bot:
    def __init__(self, iq_option):
        print("MACRSI (MA, RSI & MACD) IS OPERATING")
        self.iq = iq_option
        bot.strategy(self)

    def strategy(self):
        asset_id = "EURUSD"  # Replace with the ID of the desired asset
        timeWait = 60
        onLoose = False

        # Retrieve the latest candlestick data for the specified asset and timeframe
        rates = self.iq.get_symbol_rates(asset_id)

        # Calculate the moving average, RSI, and MACD indicators for the candles
        ma = ti.SMA(rates["Close"], timeperiod=10)
        rsi = ti.RSI(rates["Close"], timeperiod=14)
        macd, macdsignal, macdhist = ti.MACD(
            rates["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

        # Determine whether to place a call or put option based on the indicators
        if rates["Close"][-1] > ma[-1] and rsi[-1] > 50 and macd[-1] > macdsignal[-1]:
            # Place a call option
            if (self.iq.loss_stopper() or onLoose):
                onLoose = False
                timeWait = 60
                self.iq.order_sender(asset_id, "call", 1, 100)
            else:
                onLoose = True
                timeWait = 135
        elif rates["Close"][-1] < ma[-1] and rsi[-1] < 50 and macd[-1] < macdsignal[-1]:
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
