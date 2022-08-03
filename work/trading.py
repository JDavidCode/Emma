import datetime
import pytz
import time
import MetaTrader5 as mt5
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import tti
register_matplotlib_converters()

stock = ['EURUSD', 'EURNZD', 'EURAUD', 'EURCHF',
         'EURCAD', 'EURGBP', 'GBPCHF', 'GBPCAD',
         'GBPAUD', 'GBPNZD', 'GBPUSD', 'AUDUSD',
         'AUDNZD', 'AUDCHF', 'AUDCAD', 'NZDCAD',
         'NZDCHF', 'NZDUSD', 'USDCAD', 'USDCHF',
         'USDCNH', 'USDRUB', 'USDSEK']

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
        account = 61383723
        pw = "puow2tua"
        try:
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
        except:
            pass

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
            print('Error in spread f', symbol)
            return False
        if type(ask) != float or type(bid) != float:
            return False
        if (ask - 0.0001) < bid:
            return True
        else:
            return False

    def orderChecker(symbol, v):
        try:
            p = mt5.positions_get(symbol=symbol)
        except:
            return False
        plen = len(p)-1
        if p == ():
            return True
        else:
            if p[plen][9] == v:
                return False
            if p[plen][9] != v:
                return True

    def entryBreak(symbol, m, s):
        zone = pytz.timezone('Europe/Kiev')
        date_to = datetime.datetime.now().astimezone(zone).replace(tzinfo=None)
        date_from = date_to - datetime.timedelta(hours=6)
        deals = mt5.history_deals_get(
            date_from,
            date_to,
            group="*{}*".format(symbol)
        )
        dlen = len(deals)-1
        if deals != ():
            if deals[dlen][13] <= -0.1:
                date = deals[dlen][2]
                date = datetime.datetime.fromtimestamp(
                    date).astimezone(zone).replace(tzinfo=None)
                x = date_to - datetime.timedelta(minutes=m, seconds=s)
                if x > date:
                    return True
                else:
                    return False
        else:
            return True

    def symbolRates(symbol, count, time):
        rates = mt5.copy_rates_from_pos(
            symbol,
            time,
            0,
            count
        )
        rates = pd.DataFrame(rates)
        # df = pd.DataFrame(rates, columns=[
        #   'Open Time', 'Open', 'High', 'Low', 'Close', 'Tick Volume', 'Spread', 'Real Volume'])
        # print(df)
        rates['time'] = pd.to_datetime(rates['time'], unit='s')
        rates['DateTime'] = pd.DatetimeIndex(
            pd.to_datetime(rates['time'], unit='s'))
        rates = rates.set_index('DateTime')

        mm = tti.indicators.MovingAverage(input_data=rates, period=1)
        mm7 = tti.indicators.MovingAverage(
            input_data=rates, period=7, ma_type='simple')
        mm15 = tti.indicators.MovingAverage(
            input_data=rates, period=15, ma_type='simple')
        mm25 = tti.indicators.MovingAverage(
            input_data=rates, period=25, ma_type='simple')
        mmt12 = tti.indicators.Momentum(
            input_data=rates, period=12)
        cci10 = tti.indicators.CommodityChannelIndex(
            input_data=rates, period=10)
        rsi10 = tti.indicators.RelativeStrengthIndex(
            input_data=rates, period=12)
        nvps15 = tti.indicators.Envelopes(
            input_data=rates, period=15, shift=0.001)
        bbs40 = tti.indicators.BollingerBands(
            input_data=rates, period=40, std_number=2)

        rates['mm'] = mm.getTiData()
        rates['mm7'] = mm7.getTiData()
        rates['mm15'] = mm15.getTiData()
        rates['mm25'] = mm25.getTiData()
        rates['mmt12'] = mmt12.getTiData()
        rates['cci10'] = cci10.getTiData()
        rates = trading.RSI(rates)

        # rates['nvps15'] = nvps15.getTiData()
        # rates['bbs40'] = bbs40.getTiData()
        return rates

    def RSI(rates):
        rates['delta'] = delta = rates['close'].diff()
        delta = delta[1:]
        rates['Bull'] = delta.clip(lower=0)
        rates['Bear'] = -1*delta.clip(upper=0)
        ema_Bull = rates['Bull'].ewm(com=10, adjust=False).mean()
        ema_Bear = rates['Bear'].ewm(com=10, adjust=False).mean()
        Relative_Strengh = ema_Bull/ema_Bear
        rates['rsi10'] = 100 - (100/(1+Relative_Strengh))
        return rates

    def signal_5M(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_M5)
        rlen = len(rates)-1
        type = ''

        if rates['mm25'][rlen] < rates['mm15'][rlen] and rates['mm15'][rlen] < rates['mm7'][rlen] and rates['mm7'][rlen] < rates['mm'][rlen]:
            if rates['rsi10'][rlen] > 50 and rates['rsi10'][rlen] < 70:
                if rates['open'][rlen-1] < rates['close'][rlen-1] and rates['open'][rlen-1] > rates['mm7'][rlen-1] and rates['close'][rlen-1] > rates['mm7'][rlen-1]:
                    type = 'buy'
                    return type

        elif rates['mm25'][rlen] > rates['mm15'][rlen] and rates['mm15'][rlen] > rates['mm7'][rlen] and rates['mm7'][rlen] > rates['mm'][rlen]:
            if rates['rsi10'][rlen] < 50 and rates['rsi10'][rlen] > 30:
                if rates['open'][rlen-1] > rates['close'][rlen-1] and rates['open'][rlen-1] < rates['mm7'][rlen-1] and rates['close'][rlen-1] < rates['mm7'][rlen-1]:
                    type = 'sell'
                    return type
        return type

    def signal_15M(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_M15)
        rlen = len(rates)-1
        type = ''

        if rates['open'][rlen] > rates['mm15'][rlen] and rates['close'][rlen-1] > rates['mm15'][rlen-1] and rates['open'][rlen] < rates['mm'][rlen] and rates['cci10'][rlen] > 140:
            if rates['open'][rlen-1] < rates['close'][rlen-1] and rates['mmt12'][rlen-1] > 100.10 and rates['mmt12'][rlen] < 100.30:
                type = 'buy'
                return type
        elif rates['open'][rlen] < rates['mm15'][rlen] and rates['close'][rlen-1] < rates['mm15'][rlen-1] and rates['open'][rlen] > rates['mm'][rlen] and rates['cci10'][rlen] < -140:
            if rates['open'][rlen-1] > rates['close'][rlen-1] and rates['mmt12'][rlen-1] < 99.90 and rates['mmt12'][rlen] > 99.70:
                type = 'sell'
                return type
        return type

    def signal_1H(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_M15)
        rlen = len(rates)-1
        return

    def orderSender(symbol, t, lot, tp, sl, s):
        ask = mt5.symbol_info_tick(symbol).ask
        stopLoss = 0.0
        takeProfit = 0.0
        orderType = ''
        meth = ''
        if lot == 0.2:
            meth = 'Method MA'
        if lot == 0.1:
            meth = 'Method MOMENTUM'

        if t == '':
            return

        if t == 'buy':
            orderType = mt5.ORDER_TYPE_BUY
            stopLoss = ask - sl
            takeProfit = ask + tp
        elif t == 'sell':
            orderType = mt5.ORDER_TYPE_SELL
            stopLoss = ask + sl
            takeProfit = ask - tp

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
            "type_filling": mt5.ORDER_FILLING_RETURN
        }
        result = mt5.order_send(request)
        result = result._asdict()
        if result['comment'] == 'Request executed' and s == 1:
            print(symbol, t, result['comment'], meth)
        elif result['comment'] == 'Request executed' and s == 2:
            return print(symbol, t, result['comment'], meth, t)
        else:
            return print(symbol, result['comment'], meth, t)

    def orderUpdater(symbol):
        try:
            orderData = mt5.positions_get(symbol=symbol)
            if orderData == ():
                return
        except:
            return

        key = False
        stopLoss = 0.0
        takeProfit = 0.0
        try:
            for i in orderData:
                ticker = orderData[0]
                t = orderData[5]
                stopLoss = orderData[11]
                takeProfit = orderData[12]
                currentPrice = orderData[13]
                stopLoss = round(stopLoss, 5)
                takeProfit = round(takeProfit, 5)

                if i[9] == 0.1:
                    if t == 0:
                        if (currentPrice - 0.0060) > stopLoss:
                            stopLoss += 0.00045
                            takeProfit += 0.00005
                            key = True
                    elif t == 1:
                        if (currentPrice + 0.00060) < stopLoss:
                            stopLoss -= 0.00045
                            takeProfit -= 0.00005
                            key = True

                if i[9] == 0.2:
                    if t == 0:
                        if (currentPrice - 0.0012) > stopLoss:
                            stopLoss += 0.0007
                            takeProfit += 0.0001
                            key = True
                    elif t == 1:
                        if (currentPrice + 0.0012) < stopLoss:
                            stopLoss -= 0.0007
                            takeProfit -= 0.0001
                            key = True
                if key:
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": ticker,
                        "sl": stopLoss,
                        "tp": takeProfit
                    }
                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        print("{} Order Updater failed, position #{}".format(
                            symbol, ticker))
                    else:
                        print("{} Position #{} has been update".format(
                            symbol, ticker))
                else:
                    return
        except:
            print('An except has ocurred on orderUpdater f')
            return

    def orderCloser():
        orderData = mt5.positions_get()
        x = 0.0

        if orderData == ():
            return

        for i in orderData:
            x += i[15]

        try:
            if x > 25.0 or x < -20.0:
                for i in orderData:
                    ticker = i[0]
                    t = i[5]
                    symbol = i[16]
                    lot = i[9]
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
                        "price": i[13],
                        "deviation": 20,
                        "magic": 234000,
                        "comment": "python script close",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                    }
                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        print("{} Order closer failed, position #{}".format(
                            symbol, ticker))
                    else:
                        print("{} Position #{} has been closed".format(
                            symbol, ticker))
        except:
            print('An except has ocurred on orderCloser f')
            pass

    def run():
        trading.initialize()
        for i in stock:
            spread = trading.spread(i)
            if spread:
                if trading.orderChecker(i, 0.2):
                    t = trading.signal_5M(i)
                    b = trading.entryBreak(i, 0, 30)
                    if b == True:
                        trading.orderSender(i, t, 0.2, 0.0004, 0.0003, 1)
                    else:
                        pass
                if trading.orderChecker(i, 0.1):
                    t = trading.signal_15M(i)
                    b = trading.entryBreak(i, 5, 0)
                    if b == True:
                        trading.orderSender(i, t, 0.1, 0.002, 0.0006, 2)
                    trading.orderUpdater(i)
            trading.orderCloser()
            time.sleep(0.2)


if __name__ == '__main__':
    while True:
        trading.run()

        # Esto es un comentario de Prueba
