import MetaTrader5 as mt5
import time
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from pip import main
register_matplotlib_converters()

stock = ['EURUSD', 'EURNZD', 'EURAUD', 'EURCHF',
         'EURCAD', 'EURGBP', 'GBPCHF', 'GBPCAD',
         'GBPAUD', 'GBPNZD', 'GBPUSD', 'AUDUSD',
         'AUDNZD', 'AUDCHF', 'AUDCAD', 'NZDCAD',
         'NZDCHF', 'NZDUSD', 'USDCAD', 'USDCHF',
         'USDCNH', 'USDRUB', 'USDSEK', 'CADCHF']

stock2 = {
    'world': ['EURUSD', 'EURNZD', 'EURAUD', 'EURCHF',
              'EURCAD', 'EURGBP', 'GBPCHF', 'GBPCAD',
              'GBPAUD', 'GBPNZD', 'GBPUSD', 'AUDUSD',
              'AUDNZD', 'AUDCHF', 'AUDCAD', 'NZDCAD',
              'NZDCHF', 'NZDUSD', 'USDCAD', 'USDCHF',
              'USDCNH', 'USDRUB', 'USDSEK', 'CADCHF'
              ],
    'Asia': ['AUDJPY', 'CADJPY', 'CHFJPY',
             'EURJPY', 'GBPJPY', 'NZDJPY',
             'USDJPY']
}

dataFormat = {
    'World': {
        'spread': 0.00012,
        'mTDif': 0.00080,
        'mTRang': 0.00005,
        'TDif': 0.00025,
        'tp': 0.00120,
        'sl': 0.00070,
        'updaterTp': 0.00070,
        'updaterSl': 0.00080,
        'updaterPrice': 0.00090
    },
    'Asia': {
        'spread': 000.012,
        'mTDif': 000.080,
        'mTRang': 000.005,
        'TDif': 000.025,
        'tp': 000.120,
        'sl': 000.070,
        'updaterTp': 000.070,
        'updaterSl': 000.080,
        'updaterPrice': 000.090
    }

}


class trading:
    def __init__():
        pass

    def initialize():
        path = r"C:\\Program Files\\MetaTrader 5\\terminal64.exe"
        account = 5004966737
        pw = "6pjfgplj"
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
            print('Account Info')
            print(df)
        else:
            print('failed to connect to trade account')

        totalSymbols = mt5.symbols_total()
        if totalSymbols > 0:
            print("\n"+"Total symbols =", totalSymbols)
        else:
            print("symbols not found")

    def totalOrders():
        orders = mt5.orders_total()
        print('Total Orders:', orders)
        return

    def terminalInf():
        terminal_info = mt5.terminal_info()
        if terminal_info != None:
            # convert the dictionary into DataFrame and print
            terminal_info_dict = mt5.terminal_info()._asdict()
            df = pd.DataFrame(list(terminal_info_dict.items()),
                              columns=['property', 'value'])
            print('terminal information as dataframe:')
            print(df)

    def shutdown():
        return mt5.shutdown()

    def getSymbol(index):
        symbol = mt5.symbols_get("*{}*".format(index))
        print('Found symbols: ', len(symbol))
        for s in symbol:
            print(s.name)

    def spread(symbol):
        try:
            ask = mt5.symbol_info_tick(symbol).ask
            bid = mt5.symbol_info_tick(symbol).bid
        except:
            return False
        if type(ask) != float or type(bid) != float:
            return False
        if (ask - 0.00015) > bid:
            return False
        else:
            return True

    def symbolRates(symbol):
        count = 90
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

    def MVL20(rates):
        rates['MVL20'] = rates['close'].rolling(window=20).mean()
        return rates

    def MVL8(rates):
        rates['MVL12'] = rates['close'].rolling(window=12).mean()
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

    def signal(rates):
        rlen = len(rates)-1
        mlen = rlen-15
        tlen = rlen-4
        type = 'No signal'

        # MAIN TENDENCY
        MTminPrice = rates['close'][mlen]
        MTminPos = 0
        MTmajPrice = 0.00000
        MTmajPos = 0
        mainTrend = 2

        # SHORT TENDENCY
        TminPrice = rates['close'][mlen]
        TminPos = 0
        TmajPrice = 0.00000
        TmajPos = 0
        trend = 2

        # DEFINE A LARGE TIME TENDENCY (VERY-DYNAMIC) BETA
        for i in range(mlen, tlen):
            if rates['close'][i] > MTmajPrice:
                MTmajPrice = round(rates['close'][i], 5)
                MTmajPos = i
            if rates['close'][i] < MTminPrice:
                MTminPrice = round(rates['close'][i], 5)
                MTminPos = i

        if MTmajPos > MTminPos:
            xPos = MTmajPos-MTminPos
            xDif = MTmajPrice-MTminPrice
            if xPos > 7 and xPos and xDif > 0.00200:
                mainTrend = 0
        if MTminPos > MTmajPos:
            xPos = MTminPos-MTmajPos
            xDif = MTminPrice-MTmajPrice
            if xPos > 7 and xPos and xDif > -0.00200:
                mainTrend = 1

        # DEFINE A SHORT TIME TENDENCY (VERY-DYNAMIC) BETA
        for i in range(tlen, rlen):
            if rates['close'][i] > TmajPrice or rates['close'][i] + 0.00010 > TmajPrice:
                TmajPrice = round(rates['close'][i], 5)
                TmajPos = i
            if rates['close'][i] < TminPrice or rates['close'][i] - 0.00010 < MTminPrice:
                TminPrice = round(rates['close'][i], 5)
                TminPos = i

        if TmajPos > TminPos:
            xPos = TmajPos-TminPos
            xDif = TmajPrice-TminPrice
            if xPos > 2 and (xDif > 0.00040 and xDif < 0.000100):
                trend = 0
        if TminPos > TmajPos:
            xPos = TminPos-TmajPos
            xDif = TminPrice-TmajPrice
            if xPos > 2 and (xDif < -0.00040 and xDif > -0.000100):
                trend = 1

        print('MainTrend:', MTmajPrice, MTminPrice, mainTrend)
        print('Trend: ', TmajPrice, TminPrice, trend)

        # DEFINE A SHORT TREND
        # if rates['close'][rlen] > rates['open'][tlen]:
        #    c = rates['close'][rlen] - rates['close'][tlen]
        #    if c > 0.00015 and c < 0.00030:
        #        trend = 0
        # elif rates['close'][rlen] < rates['open'][tlen]:
        #    c = rates['close'][rlen] - rates['close'][tlen]
        #    if c < -0.00015 and c > -0.00030:
        #        trend = 1

        #print(mainTrend, trend)
        if mainTrend == 2 or trend == 2:
            return

        # DEFINE SIGNAL
        if mainTrend == 0 and trend == 0 and (rates['RSI'][rlen] < 70.0) and rates['close'][tlen] > rates['MVL12'][rlen]:
            type = 'buy'
            return type

        if mainTrend == 1 and trend == 1 and (rates['RSI'][rlen] > 30.0) and rates['close'][tlen] < rates['MVL12'][rlen]:
            type = 'sell'
            return type
        else:
            return type

    def showGraphichs(rates):
        fig, axe = plt.subplots(2, 1)
        axe[0].plot(rates['close'], label='Symbol')
        axe[0].plot(rates['MVL20'], label='Media Movil 20')
        axe[0].plot(rates['MVL12'], label='Media Movil 12')
        axe[1].plot(rates['RSI'], color='b')

        plt.plot(rates['RSI'], label='RSI')

        axe[1].axhline(y=30, color='r', linewidth=3)
        axe[1].axhline(y=50, color='black', linewidth=2)
        axe[1].axhline(y=70, color='r', linewidth=3)
        plt.tight_layout()
        fig.autofmt_xdate()
        plt.show()

    def orderChecker(symbol):
        p = mt5.positions_get(symbol=symbol)
        key = bool
        if p == ():
            key = True
        elif len(p) > 0:
            key = False
        return key

    def orderSender(symbol, lot, t):
        ask = mt5.symbol_info_tick(symbol).ask
        stopLoss = 0.0
        takeProfit = 0.0
        orderType = 'null'

        if t == 'buy':
            orderType = mt5.ORDER_TYPE_BUY
            stopLoss = ask - 0.00070
            takeProfit = ask + 0.00120
            print(symbol, 'Buying')
        elif t == 'sell':
            orderType = mt5.ORDER_TYPE_SELL
            stopLoss = ask + 0.00070
            takeProfit = ask - 0.00120
            print(symbol, 'selling')
        else:
            return

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": orderType,
            "price": ask,
            "sl": stopLoss,
            "tp": takeProfit,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        result = mt5.order_send(request)
        result = result._asdict()
        return print(result['comment'])

    def orderUpdater(symbol):
        orderData = mt5.positions_get(symbol=symbol)
        x = 0
        key = False
        stopLoss = 0.0
        takeProfit = 0.0
        for i in orderData:
            ticker = orderData[x][0]
            t = orderData[x][5]
            stopLoss = orderData[x][11]
            takeProfit = orderData[x][12]
            currentPrice = orderData[x][13]
            stopLoss = round(stopLoss, 5)
            takeProfit = round(takeProfit, 5)
            if t == 0:
                if (currentPrice - 0.00090) > stopLoss:
                    stopLoss += 0.00080
                    takeProfit += 0.00070
                    key = True
            elif t == 1:
                if (currentPrice + 0.00090) < stopLoss:
                    stopLoss -= 0.00080
                    takeProfit -= 0.00070
                    key = True
        if key:
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticker,
                "sl": stopLoss,
                "tp": takeProfit
            }
            mt5.order_send(request)
            return print('{} Order #{} has been update'.format(symbol, ticker))
        else:
            return

    def orderCloser(symbol):
        orderData = mt5.positions_get(symbol=symbol)
        x = 0
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
            elif currentProfit >= 2.25:
                result = mt5.order_send(request)
            else:
                return

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return print("Order Send failed, retcode={}".format(result.retcode))
            else:
                return print("Position #{} has been closed".format(ticker))

    def run():
        trading.initialize()
        for i in stock:
            key = trading.orderChecker(i)
            spread = trading.spread(i)
            if key and spread:
                print(i)
                r = trading.symbolRates(i)
                s = trading.signal(r)
                trading.orderSender(i, 0.05, s)
            else:
                pass
            for y in stock:
                trading.orderUpdater(y)
            time.sleep(0.5)


if __name__ == '__main__':
    while True:
        trading.run()
    # trading.initialize()
    #r = trading.symbolRates('GBPCAD')
    # trading.signal(r)
    # trading.showGraphichs(r)
    # trading.shutdown()
