from trading_core import tradingIqOption, ti, time, np


class bot:
    def __init__(self, iq_option):
        print("MASR (MA, SUPPORT & RESISTANCE) IS OPERATING")
        self.iq = iq_option
        bot.strategy(self)

    def strategy(self):
        asset_id = "EURUSD"
        timeWait = 60
        onLoose = False
        rates = self.iq.get_symbol_rates(asset_id)

        # Calculate the MA and Support/Resistance levels
        rates['MA'] = rates['Close'].rolling(window=20).mean()
        rates['Support'] = rates['Low'].rolling(window=50).min()
        rates['Resistance'] = rates['High'].rolling(window=50).max()

        # Get the current price
        current_price = rates["Close"][-1]

        # Determine if we should place a trade
        if current_price > rates['MA'][-1] and current_price > rates['Support'][-1]:
            # Place a call option
            if (self.iq.loss_stopper() or onLoose):
                onLoose = False
                timeWait = 60
                self.iq.order_sender(asset_id, "call", 1, 100)
            else:
                onLoose = True
                timeWait = 135
        elif current_price < rates['MA'][-1] and current_price < rates['Resistance'][-1]:
            # Place a put option
            if (self.iq.loss_stopper() or onLoose):
                onLoose = False
                timeWait = 60
                self.iq.order_sender(asset_id, "put", 1, 100)
            else:
                onLoose = True
                timeWait = 135
        elif current_price >= rates['Support'][-1] and current_price <= rates['Resistance'][-1]:
            # Do not enter a trade
            print("No trade Option")
        else:
            print("No trade Option")
        # Wait 1 minute before checking the indicators again
        time.sleep(timeWait)


if __name__ == "__main__":
    pass
