from trading_core import tradingIqOption, ti, time, np


class Macrsi:
    def strategy(dataset):
        # Calculate the moving average, RSI, and MACD indicators for the candles
        ma = ti.SMA(dataset["Close"], timeperiod=10)
        rsi = ti.RSI(dataset["Close"], timeperiod=14)
        macd, macdsignal, macdhist = ti.MACD(
            dataset["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

        # Determine whether to place a call or put option based on the indicators
        if dataset["Close"][-1] < ma[-1] and rsi[-1] < 50 and macd[-1] < macdsignal[-1]:
            # Place a put option
            return ['put', 1]
        elif dataset["Close"][-1] > ma[-1] and rsi[-1] > 50 and macd[-1] > macdsignal[-1]:
            # Place a call option
            return ['call', 1]

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
            return ['put', 5]
        elif current_price > dataset['MA'][-1] and current_price > dataset['Support'][-1]:
            # Place a call option
            return ['call', 5]
        elif current_price >= dataset['Support'][-1] and current_price <= dataset['Resistance'][-1]:
            # Do not enter a trade
            return 0
        else:
            return 0


class Mrsic:
    def strategy(dataset):
        # Calculate RSI and CCI indicators
        rsi = ti.RSI(dataset["Close"], timeperiod=14)
        cci = ti.CCI(dataset["High"], dataset["Low"],
                     dataset["Close"], timeperiod=20)

        # Calculate Moving Averages
        short_ma = dataset["Close"].rolling(window=5).mean()
        long_ma = dataset["Close"].rolling(window=20).mean()
        # Check conditions and make a trade decision
        last_rsi = rsi[-1]
        last_cci = cci[-1]
        last_close = dataset["Close"][-1]
        last_short_ma = short_ma[-1]
        last_long_ma = long_ma[-1]

        if last_close < last_short_ma and last_close < last_long_ma and last_rsi > 70 and last_cci > 100:
            # Place a put option
            return ['put', 9]
        elif last_close > last_short_ma and last_close > last_long_ma and last_rsi < 30 and last_cci < -100:
            # Place a call option
            return ['put', 9]

        else:
            return 0


if __name__ == "__main__":
    pass
