from trading_core import tradingIqOption, ti, time, np


class Macrsi:
    def strategy(dataset):
        # Calculate the moving average, RSI, and MACD indicators for the dataset
        ma = ti.SMA(dataset["Close"], timeperiod=10)
        rsi = ti.RSI(dataset["Close"], timeperiod=14)
        macd, macdsignal, macdhist = ti.MACD(
            dataset["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

        # Determine whether to place a call or put option based on the indicators
        if dataset["Close"][-1] < ma[-1] and rsi[-1] < 50 and macd[-1] < macdsignal[-1]:
            # Place a put option
            return ['put', 2]
        elif dataset["Close"][-1] > ma[-1] and rsi[-1] > 50 and macd[-1] > macdsignal[-1]:
            # Place a call option
            return ['call', 2]

        else:
            return 0


class Masr:
    def strategy(dataset):
        # Calculate the MA and Support/Resistance levels
        dataset['MA'] = dataset['Close'].rolling(window=20).mean()
        dataset['Support'] = dataset['Low'].rolling(window=50).min()
        dataset['Resistance'] = dataset['High'].rolling(window=50).max()

        # Get the current price
        current_price = dataset["Close"][-1]

        # Determine if we should place a trade
        if current_price < dataset['MA'][-1] and current_price < dataset['Resistance'][-1]:
            # Place a put option
            return ['put', 2]
        elif current_price > dataset['MA'][-1] and current_price > dataset['Support'][-1]:
            # Place a call option
            return ['call', 2]
        elif current_price >= dataset['Support'][-1] and current_price <= dataset['Resistance'][-1]:
            # Do not enter a trade
            return 0
        else:
            return 0


class Mrsic:
    def strategy(dataset):

        close_prices = np.array([candle for candle in dataset["Close"]])

        # Calculate Indicators
        rsi = ti.RSI(close_prices, 14)
        upper, middle, lower = ti.BBANDS(
            close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        mom = ti.MOM(close_prices, timeperiod=14)
        sar = ti.SAR(dataset["High"], np.array(
            dataset["Low"]), acceleration=0.02, maximum=0.2)

        # Check Trading Conditions
        if rsi[-1] < 30 and close_prices[-1] < lower[-1] and mom[-1] < 0 and close_prices[-2] > sar[-2]:
            return ['call', 5]
        elif rsi[-1] > 70 and close_prices[-1] > upper[-1] and mom[-1] > 0 and close_prices[-2] < sar[-2]:
            return ['put', 5]
        else:
            return 0


if __name__ == "__main__":
    pass
