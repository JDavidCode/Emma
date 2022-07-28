import MetaTrader5 as mt5
import time
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import tti
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
        account = 61208305
        pw = "mrkff7vr"
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
            return False
        if type(ask) != float or type(bid) != float:
            return False
        if (ask - 0.00008) > bid:
            return False
        else:
            return True

    def symbolRates(symbol):
        count = 60
        rates = mt5.copy_rates_from_pos(
            symbol,
            mt5.TIMEFRAME_M5,
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
        mm5 = tti.indicators.MovingAverage(
            input_data=rates, period=5, ma_type='simple')
        mm15 = tti.indicators.MovingAverage(
            input_data=rates, period=15, ma_type='simple')
        mm30 = tti.indicators.MovingAverage(
            input_data=rates, period=30, ma_type='simple')
        mmt16 = tti.indicators.Momentum(
            input_data=rates, period=16)
        cci10 = tti.indicators.CommodityChannelIndex(
            input_data=rates, period=10)
        nvps15 = tti.indicators.Envelopes(
            input_data=rates, period=15, shift=0.001)
        bbs40 = tti.indicators.BollingerBands(
            input_data=rates, period=40, std_number=2)

        rates['mm'] = mm.getTiData()
        rates['mm5'] = mm5.getTiData()
        rates['mm15'] = mm15.getTiData()
        rates['mm30'] = mm30.getTiData()
        rates['mtum16'] = mmt16.getTiData()
        rates['cci10'] = cci10.getTiData()
        # rates['nvps15'] = nvps15.getTiData()
        # rates['bbs40'] = bbs40.getTiData()
        rates = trading.RSI(rates)

        return rates

    def RSI(rates):
        rates['delta'] = delta = rates['close'].diff()
        delta = delta[1:]
        rates['Bull'] = delta.clip(lower=0)
        rates['Bear'] = -1*delta.clip(upper=0)
        ema_Bull = rates['Bull'].ewm(com=13, adjust=False).mean()
        ema_Bear = rates['Bear'].ewm(com=13, adjust=False).mean()
        Relative_Strengh = ema_Bull/ema_Bear
        rates['RSI'] = 100 - (100/(1+Relative_Strengh))
        return rates

    def signal(rates, symbol):
        rlen = len(rates)-1

        # SIGNAL METHOD 1 MAVERAGE'S 5M
        if rates['mm30'][rlen] < rates['close'][rlen] and rates['mm5'][rlen] < rates['close'][rlen] and rates['mm5'][rlen] < rates['open'][rlen] and rates['mm30'][rlen] < rates['mm15'][rlen] and rates['mm15'][rlen] < rates['mm5'][rlen] and rates['open'][rlen] < rates['mm'][rlen]:
            xDif = rates['close'][rlen] - rates['mm5'][rlen]
            if xDif < 0.00030 and rates['RSI'][rlen] > 50 and rates['RSI'][rlen] < 60:
                type = 'buy'
                print(symbol, type, 'Method MA')
                return type
        elif rates['mm30'][rlen] > rates['close'][rlen] and rates['mm5'][rlen] > rates['close'][rlen] and rates['mm5'][rlen] > rates['open'][rlen] and rates['mm30'][rlen] > rates['mm15'][rlen] and rates['mm15'][rlen] > rates['mm5'][rlen] and rates['open'][rlen] > rates['mm'][rlen]:
            xDif = rates['mm5'][rlen] - rates['close'][rlen]
            if xDif < 0.00030 and rates['RSI'][rlen] < 50 and rates['RSI'][rlen] > 40:
                type = 'sell'
                print(symbol, type, 'Method MA')
                return type
        # SIGNAL METHOD 2 MOMENTUM 15M
        if rates['mm15'][rlen] < rates['close'][rlen] and rates['mm15'][rlen] < rates['open'][rlen] and rates['open'][rlen] < rates['mm'][rlen] and rates['cci10'][rlen] > 110.0:
            if rates['mtum16'][rlen] > 100.10 and rates['mtum16'][rlen] < 100.20:
                type = 'buy'
                print(symbol, type, 'Method M0MENTUM')
                return type
        elif rates['mm15'][rlen] > rates['close'][rlen] and rates['mm15'][rlen] > rates['open'][rlen] and rates['open'][rlen] > rates['mm'][rlen] and rates['cci10'][rlen] < -110.0:
            if rates['mtum16'][rlen] < 100.05 and rates['mtum16'][rlen] > 99.95:
                type = 'sell'
                print(symbol, type, 'Method MOMENTUM')
                return type

        # SIGNAL METHOD 3

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
            stopLoss = ask - 0.00030
            takeProfit = ask + 0.00060
        elif t == 'sell':
            orderType = mt5.ORDER_TYPE_SELL
            stopLoss = ask + 0.00030
            takeProfit = ask - 0.00060
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
                if (currentPrice - 0.00060) > stopLoss:
                    stopLoss += 0.00050
                    takeProfit += 0.00010
                    key = True
            elif t == 1:
                if (currentPrice + 0.00060) < stopLoss:
                    stopLoss -= 0.00050
                    takeProfit -= 0.00010
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
                r = trading.symbolRates(i)
                s = trading.signal(r, i)
                trading.orderSender(i, 0.05, s)
            else:
                pass
            # for y in stock:
            #    trading.orderUpdater(y)
            time.sleep(0.3)


if __name__ == '__main__':
    while True:
        trading.run()
    # trading.initialize()
    # r = trading.symbolRates('GBPCAD')
    # trading.signal(r)
    # trading.showGraphichs(r)
    # trading.shutdown()
