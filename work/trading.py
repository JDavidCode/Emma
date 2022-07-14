import MetaTrader5 as mt5
import time
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

stock = ['EURUSD', 'EURNZD', 'EURAUD', 'EURCHF', 'EURGBP', 'EURCAD', 'GBPUSD', 'GBPCHF',
         'GBPCAD', 'AUDNZD', 'AUDCHF', 'AUDUSD', 'AUDCAD', 'NZDCAD', 'NZDCHF', 'NZDUSD', 'USDCAD', 'USDCHF']


class trading:
    def __init__(self) -> None:
        pass

    def initialize():
        path = r"C:\\Program Files\\MetaTrader 5\\terminal64.exe"
        account = 60900056
        pw = "bawdwz1e"
        mt5.initialize(
            path,
            login=account,
            password=pw,
            server="MetaQuotes-Demo",
            timeout=15000,
            portable=False
        )
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())

    def accountInf():
        account_info = mt5.account_info()
        if account_info != None:
            # convert the dictionary into DataFrame and print
            account_info_dict = mt5.account_info()._asdict()
            df = pd.DataFrame(list(account_info_dict.items()),
                              columns=['property', 'value'])
            print(df)
        else:
            print("failed to connect to trade account")

        totalSymbols = mt5.symbols_total()
        if totalSymbols > 0:
            print("\n"+"Total symbols =", totalSymbols)
        else:
            print("symbols not found")

    def terminalInf():
        terminal_info = mt5.terminal_info()
        if terminal_info != None:
            # convert the dictionary into DataFrame and print
            terminal_info_dict = mt5.terminal_info()._asdict()
            df = pd.DataFrame(list(terminal_info_dict.items()),
                              columns=['property', 'value'])
            print('terminal information as dataframe:')
            print(df)

    def getSymbols(index):
        symbol = mt5.symbols_get("*{}*".format(index))
        print('Found symbols: ', len(symbol))
        for s in symbol:
            print(s.name)

    def MVL20(rates):
        rates['MVL20'] = rates['close'].rolling(window=20).mean()
        return rates

    def MVL8(rates):
        rates['MVL8'] = rates['close'].rolling(window=8).mean()
        return rates

    def RSI(rates):
        rates['delta'] = delta = rates['close'].diff()
        delta = delta[1:]
        rates['Bull'] = Bull = delta.clip(lower=0)
        rates['Bear'] = Bear = -1*delta.clip(upper=0)
        ema_Bull = rates['Bull'].ewm(com=13, adjust=False).mean()
        ema_Bear = rates['Bear'].ewm(com=13, adjust=False).mean()
        Relative_Strengh = ema_Bull/ema_Bear
        rates['RSI'] = 100 - (100/(1+Relative_Strengh))
        return rates

    def symbolRates(symbol):
        count = 120
        rates = mt5.copy_rates_from_pos(
            symbol,
            mt5.TIMEFRAME_M1,
            0,
            count
        )
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame = trading.MVL20(rates_frame)
        rates_frame = trading.MVL8(rates_frame)
        rates_frame = trading.RSI(rates_frame)
        return rates_frame

    def signal(rates):
        rlen = len(rates)-1
        mlen = rlen-18
        tlen = rlen-3
        type = 'No signal'
        mainTrend = ''
        trend = ''
        if rates['close'][mlen] < (rates['close'][rlen] - 0.00050):
            mainTrend = 'mainBull'
        elif rates['close'][mlen] > (rates['close'][rlen] + 0.00050):
            mainTrend = 'mainBear'
        else:
            mainTrend = ''
            return type

        if rates['close'][tlen] < (rates['close'][rlen] - 0.00015):
            trend = 'bull'
        elif rates['close'][tlen] > (rates['close'][rlen] + 0.00015):
            trend = 'bear'
        else:
            trend = ''
            return type

        for i in range(tlen, rlen):
            if trend == 'bear':
                if (rates['close'][i] + 0.00045) < rates['MVL20'][i]:
                    if rates['MVL20'][i] > rates['MVL8'][i]:
                        type = 'sell'
                        print('Selling')
                        return type
            elif trend == 'bear':
                if (rates['close'][i] - 0.00045) > rates['MVL20'][i]:
                    if (rates['MVL20'][i] < rates['MVL8'][i]):
                        print('Buying')
                        type = 'buy'
                        return type
            else:
                return type

    def totalOrders():
        orders = mt5.orders_total()
        print('Total Orders:', orders)
        return

    def orderSender(symbol, lot, t, key):
        if key == False:
            return
        price = mt5.symbol_info_tick(symbol).ask
        price = round(price, 5)
        global stopLoss
        global takeProfit
        global orderType
        global request
        if t == 'buy':
            orderType = mt5.ORDER_TYPE_BUY
            stopLoss = price - 0.00050
            takeProfit = price + 0.00200
        elif t == 'sell':
            orderType = mt5.ORDER_TYPE_SELL
            stopLoss = price + 0.00050
            takeProfit = price - 0.00200

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": orderType,
            "price": price,
            "sl": stopLoss + 0.00001,
            "tp": takeProfit + 0.00001,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        result = mt5.order_send(request)
        result = result._asdict()
        print(result['comment'])
        return

    def orderCloser(symbol):
        orderData = mt5.positions_get(symbol=symbol)
        x = 0
        print(orderData)
        for i in orderData:
            ticker = orderData[x][0]
            t = orderData[x][5]
            lot = orderData[x][9]
            currentPrice = orderData[x][13]
            currentProfit = orderData[x][15]

            if t == 0:
                orderType = mt5.ORDER_TYPE_SELL
            elif t == 1:
                orderType = mt5.ORDER_TYPE_BUY

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": orderType,
                "position": ticker,
                "price": currentPrice,
                "deviation": 20,
                "magic": 234000,
                "comment": "python script close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN
            }

            if currentProfit <= -1.0:
                result = mt5.order_send(request)
            else:
                return

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print("Order Send failed, retcode={}".format(result.retcode))
                return
            else:
                print("Position #{} has been closed".format(ticker))

    def orderUpdater(symbol):
        orderData = mt5.positions_get(symbol=symbol)
        x = 0
        key = False
        global stopLoss
        global takeProfit
        for i in orderData:
            ticker = orderData[x][0]
            t = orderData[x][5]
            openPrice = orderData[x][10]
            stopLoss = orderData[x][11]
            takeProfit = orderData[x][12]
            currentPrice = orderData[x][13]
            stopLoss = round(stopLoss, 5)
            takeProfit = round(takeProfit, 5)
            if t == 0:
                if currentPrice > (openPrice + 0.00150):
                    stopLoss += 0.00100
                    takeProfit += 0.00050
                    key = True
            elif t == 1:
                if currentPrice < (openPrice - 0.00150):
                    stopLoss -= 0.00100
                    takeProfit -= 0.00150
                    key = True
            x += 1

            if not key:
                return
            else:
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": ticker,
                    "sl": stopLoss,
                    "tp": takeProfit
                }
                result = mt5.order_send(request)
                print(result['comment'])
            return

    def orderChecker(symbol):
        p = mt5.positions_get(symbol=symbol)
        key = bool
        if p == ():
            key = True
        elif len(p) > 0:
            key = False
        return key

    def showGraphichs(rates):
        fig, axe = plt.subplots(2, 1)
        axe[0].plot(rates['close'], label='Symbol')
        axe[0].plot(rates['MVL20'], label='Media Movil 20')
        axe[0].plot(rates['MVL8'], label='Media Movil 8')
        axe[1].plot(rates['RSI'], color='b')

        plt.plot(rates['RSI'], label='RSI')

        axe[1].axhline(y=30, color='r', linewidth=3)
        axe[1].axhline(y=50, color='black', linewidth=2)
        axe[1].axhline(y=70, color='r', linewidth=3)
        plt.tight_layout()
        fig.autofmt_xdate()
        plt.show()

    def shutdown():
        return mt5.shutdown()

    def core():
        trading.initialize()
        for i in stock:
            try:
                print(i)
                data = trading.symbolRates(i)
                key = trading.orderChecker(i)
                t = trading.signal(data)
                if t != 'No signal':
                    trading.orderSender(i, 0.01, t, key)
                trading.orderUpdater(i)
                trading.orderCloser(i)
                time.sleep(1)
            except:
                pass


if __name__ == "__init__":
    while True:
        trading.core
