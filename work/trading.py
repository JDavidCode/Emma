import datetime
import pytz
import time
import MetaTrader5 as mt5
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import tti
register_matplotlib_converters()

today_AccountBalance = 0.0
volume = 0.03

stock = ['EURUSD', 'EURNZD', 'EURAUD', 'EURCHF',
         'EURCAD', 'EURGBP', 'EURSGD', 'GBPCHF', 'GBPCAD',
         'GBPAUD', 'GBPNZD', 'GBPUSD', 'AUDUSD',
         'AUDNZD', 'AUDCHF', 'AUDCAD', 'NZDCAD',
         'NZDCHF', 'NZDUSD', 'USDCAD', 'USDCHF']


class trading:
    def __init__():
        pass

    def initialize():
        path = r"C:\\Program Files\\MetaTrader 5\\terminal64.exe"
        account = 65501987
        pw = "Aa1040492386"
        try:
            mt5.initialize(
                path,
                login=account,
                password=pw,
                server="XMGlobal-MT5 2",
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

    def timeSchedule():
        currentDay = datetime.datetime.today()
        nDate = datetime.date.today()
        timeSchedule = ['{} 8:30:30'.format(nDate), '{} 12:30:00'.format(
            nDate), '{} 19:00:00'.format(nDate), '{} 23:30:00'.format(nDate), '{} 02:00:00'.format(nDate), '{} 05:30:00'.format(nDate)]

        t0 = time.strptime(timeSchedule[0], '%Y-%m-%d %H:%M:%S')
        t0 = datetime.datetime.fromtimestamp(time.mktime(t0))

        t1 = time.strptime(timeSchedule[1], '%Y-%m-%d %H:%M:%S')
        t1 = datetime.datetime.fromtimestamp(time.mktime(t1))

        t2 = time.strptime(timeSchedule[2], '%Y-%m-%d %H:%M:%S')
        t2 = datetime.datetime.fromtimestamp(time.mktime(t2))

        t3 = time.strptime(timeSchedule[3], '%Y-%m-%d %H:%M:%S')
        t3 = datetime.datetime.fromtimestamp(time.mktime(t3))

        t4 = time.strptime(timeSchedule[4], '%Y-%m-%d %H:%M:%S')
        t4 = datetime.datetime.fromtimestamp(time.mktime(t4))

        t5 = time.strptime(timeSchedule[5], '%Y-%m-%d %H:%M:%S')
        t5 = datetime.datetime.fromtimestamp(time.mktime(t5))

        if currentDay > t0 and currentDay < t1:
            return True
        elif currentDay > t2 and currentDay < t3:
            return True
        elif currentDay > t4 and currentDay < t5:
            return True
        else:
            return False

    def spread(symbol):
        try:
            ask = mt5.symbol_info_tick(symbol).ask
            bid = mt5.symbol_info_tick(symbol).bid
        except:
            return True
        #print(ask, bid)
        if type(ask) != float or type(bid) != float:
            return False
        if (ask - 0.0003) < bid:
            return True
        else:
            return False

    def orderChecker(symbol):
        global volume
        p = mt5.positions_get(symbol=symbol)
        x = 0
        if p == ():
            return True
        elif p != ():
            for i in p:
                if i[9] == volume:
                    x += 1
        else:
            return False

        if x == 0:
            return False
        elif x > 0:
            return False
        else:
            return False

    def win_loss_Stopper():
        global today_AccountBalance
        currentBalance = mt5.account_info()
        currentBalance = currentBalance[10]
        maxLoss = today_AccountBalance-9.0
        maxWin = today_AccountBalance+23.0

        if currentBalance > maxWin:
            print('Max Win Reached From {} to {}'.format(
                today_AccountBalance, currentBalance))
            today_AccountBalance = currentBalance
            i = input('Continue Trading? Y/N ')
            if i == 'y' or i == 'Y':
                return True
            elif i == 'n' or i == 'N':
                time.sleep(600)
            else:
                return False
            return False
        elif currentBalance < maxLoss:
            print('Max Loss Reached From {} to {}'.format(
                today_AccountBalance, currentBalance))
            today_AccountBalance = currentBalance
            i = input('Continue Trading? Y/N ')
            if i == 'y' or i == 'Y':
                return True
            elif i == 'n' or i == 'N':
                time.sleep(600)
            else:
                return False
            return False

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
                    date)
                date = date + datetime.timedelta(hours=5, minutes=m)
                if date < date_to:
                    return True
                else:
                    return False
            if deals[dlen][13] >= 0.1:
                date = deals[dlen][2]
                date = datetime.datetime.fromtimestamp(
                    date)
                date = date + datetime.timedelta(hours=5, seconds=s)
                if date < date_to:
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
        mm5 = tti.indicators.MovingAverage(
            input_data=rates, period=5, ma_type='simple')
        mm12 = tti.indicators.MovingAverage(
            input_data=rates, period=12, ma_type='simple')
        mmt12 = tti.indicators.Momentum(
            input_data=rates, period=12)
        cci10 = tti.indicators.CommodityChannelIndex(
            input_data=rates, period=10)
        cci30 = tti.indicators.CommodityChannelIndex(
            input_data=rates, period=30)
        rsi16 = tti.indicators.RelativeStrengthIndex(
            input_data=rates, period=3)

        rates['mm'] = mm.getTiData()
        rates['mm5'] = mm5.getTiData()
        rates['mm12'] = mm12.getTiData()
        rates['mmt12'] = mmt12.getTiData()
        rates['cci30'] = cci30.getTiData()
        rates['cci10'] = cci10.getTiData()
        #rates['rsi16'] = rsi16.getTiData()
        rates = trading.RSI(rates)

        # rates['nvps15'] = nvps15.getTiData()
        # rates['bbs40'] = bbs40.getTiData()
        return rates

    def RSI(rates):
        rates['delta'] = delta = rates['close'].diff()
        delta = delta[1:]
        rates['Bull'] = delta.clip(lower=0)
        rates['Bear'] = -1*delta.clip(upper=0)
        ema_Bull = rates['Bull'].ewm(com=16, adjust=False).mean()
        ema_Bear = rates['Bear'].ewm(com=16, adjust=False).mean()
        Relative_Strengh = ema_Bull/ema_Bear
        rates['rsi16'] = 100 - (100/(1+Relative_Strengh))
        return rates

    def showGraphichs(rates, t):
        if t == 'M1':
            fig, axe = plt.subplots(3, 1)
            axe[0].plot(rates['close'], label='Symbol')
            axe[0].plot(rates['mm5'], label='Media Movil 7')
            axe[0].plot(rates['mm12'], label='Media Movil 15')
            axe[0].plot(rates['mm25'], label='Media Movil 25')
            axe[1].plot(rates['rsi16'], color='b')
            axe[2].plot(rates['cci30'], color='green')

            plt.plot(rates['rsi16'], label='RSI')
            axe[1].axhline(y=30, color='r', linewidth=1)
            axe[1].axhline(y=50, color='r', linewidth=1)
            axe[1].axhline(y=70, color='r', linewidth=1)

            plt.plot(rates['cci30'], label='cci')
            axe[2].axhline(y=100, color='b', linewidth=1)
            axe[2].axhline(y=0, color='b', linewidth=1)
            axe[2].axhline(y=-100, color='b', linewidth=1)
        elif t == 'M15':
            fig, axe = plt.subplots(3, 1)
            axe[0].plot(rates['close'], label='Symbol')
            axe[0].plot(rates['mm12'], label='Media Movil 15')
            axe[1].plot(rates['mmt12'], color='b')
            axe[2].plot(rates['cci10'], color='green')

            plt.plot(rates['mmt12'], label='MOMENTUM')
            axe[1].axhline(y=100.20, color='r', linewidth=1)
            axe[1].axhline(y=100, color='r', linewidth=1)
            axe[1].axhline(y=99.80, color='r', linewidth=1)

            plt.plot(rates['cci10'], label='cci')
            axe[2].axhline(y=100, color='b', linewidth=1)
            axe[2].axhline(y=0, color='b', linewidth=1)
            axe[2].axhline(y=-100, color='b', linewidth=1)

        plt.tight_layout()
        fig.autofmt_xdate()
        plt.show()


    def signal_15M(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_M30)
        rlen = len(rates)-2
        type = ''

        if rates['mm5'][rlen] > rates['mm12'][rlen] and rates['mm'][rlen] > rates['mm5'][rlen] and rates['close'][rlen] > rates['mm5'][rlen]:
            backward = float(
                round(rates['high'][rlen], 5) - round(rates['close'][rlen], 5))
            #print(symbol, 'MM PASS')
            if rates['mmt12'][rlen] < 100.15 and rates['mmt12'][rlen-1] < rates['mmt12'][rlen] and backward < 0.00020:
                #print(symbol, 'mmt12 and backward PASS')
                type = 'buy'
                return type

        if rates['mm12'][rlen] > rates['mm5'][rlen] and rates['mm5'][rlen] > rates['mm'][rlen] and rates['mm5'][rlen] > rates['close'][rlen]:
            backward = float(
                round(rates['close'][rlen], 5) - round(rates['low'][rlen], 5))
            #print(symbol, 'MM PASS')
            if rates['mmt12'][rlen] > 99.85 and rates['mmt12'][rlen] > rates['mmt12'][rlen-1] and backward < 0.00020:
                #print(symbol, 'mmt12 and backward PASS')
                type = 'sell'
                return type
        return type

    def signal_1H(symbol):
        rates = trading.symbolRates(symbol, 60, mt5.TIMEFRAME_H1)
        rlen = len(rates)-2
        type = ''

        if rates['open'][rlen] > rates['mm12'][rlen] and rates['close'][rlen] > rates['mm12'][rlen] and rates['mm'][rlen] > rates['mm12'][rlen] and rates['cci10'][rlen] > 0 and rates['cci10'][rlen] < 125:
            backward = float(
                round(rates['high'][rlen], 5) - round(rates['close'][rlen], 5))
            if rates['mmt12'][rlen-1] < rates['mmt12'][rlen] and rates['mmt12'][rlen] > 100.0 and rates['mmt12'][rlen] < 100.20 and backward < 0.0007:
                type = 'buy'
                return type
        elif rates['open'][rlen] < rates['mm12'][rlen] and rates['close'][rlen] < rates['mm12'][rlen] and rates['mm'][rlen] > rates['mm12'][rlen] and rates['cci10'][rlen] < 0 and rates['cci10'][rlen] > -125:
            backward = float(
                round(rates['close'][rlen], 5) - round(rates['low'][rlen], 5))
            if rates['mmt12'][rlen-1] > rates['mmt12'][rlen] and rates['mmt12'][rlen] < 100.0 and rates['mmt12'][rlen] > 99.80 and backward < 0.0007:
                type = 'sell'
                return type
        return type

    def orderSender(symbol, t, lot, tp, sl, s):
        ask = mt5.symbol_info_tick(symbol).ask
        bid = mt5.symbol_info_tick(symbol).bid
        stopLoss = 0.0
        takeProfit = 0.0
        orderType = ''
        meth = ''

        if t == '':
            return

        if t == 'buy':
            orderType = mt5.ORDER_TYPE_BUY
            stopLoss = ask - sl
            takeProfit = bid + tp
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
            "type_filling": mt5.ORDER_FILLING_IOC
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
                ticker = i[0]
                t = i[5]
                stopLoss = round(i[11], 5)
                takeProfit = round(i[12], 5)
                currentPrice = i[13]
                if t == 0:
                    if (currentPrice - 0.00150) > stopLoss:
                        stopLoss = currentPrice - 0.0006
                        takeProfit = takeProfit + 0.0003
                        key = True
                elif t == 1:
                    if (currentPrice + 0.00150) < stopLoss:
                        stopLoss = currentPrice + 0.0006
                        takeProfit = takeProfit - 0.0003
                        key = True

                if key:
                    #print(stopLoss, takeProfit)
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
        global volume
        orderData = mt5.positions_get()
        x = 0.0
        if orderData == ():
            return
        for i in orderData:
            x += i[15]
        try:
            if x > 20.0 or x < -10.0:
                for i in orderData:
                    if volume in i:
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
                            "type_filling": mt5.ORDER_FILLING_IOC
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

    def core():
        global volume
        for i in stock:
            if trading.timeSchedule() and trading.win_loss_Stopper():
                if trading.spread(i) and trading.orderChecker(i):
                    t = trading.signal_1H(i)
                    b = trading.entryBreak(i, 5.0, 0.0)
                    if b == True:
                        trading.orderSender(
                            i, t, volume, 0.0055, 0.002, 2)
                    else:
                        pass
                if trading.spread(i) and trading.orderChecker(i):
                    t = trading.signal_15M(i)
                    b = trading.entryBreak(i, 1.0, 15.0)
                    if b == True:
                        trading.orderSender(
                            i, t, volume, 0.0025, 0.001, 1)
                    else:
                        pass
            # trading.orderUpdater(i)
            # trading.orderCloser()
        time.sleep(0.3)

    def awake():
        global today_AccountBalance
        trading.initialize()
        symbols = mt5.symbols_get()
        print('Symbols: ', len(symbols))
        count = 0
        # display the first five ones
        for s in symbols:
            count += 1
            print("{}. {}".format(count, s.name))
            if count == 75:
                break
        print()
        accountBalance = mt5.account_info()
        today_AccountBalance = accountBalance[13]
        trading.accountInf()

    def run():
        trading.awake()
        while True:
            trading.core()



if __name__ == '__main__':
    trading.run()
