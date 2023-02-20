import datetime
from turtle import update
import pytz
import time
import MetaTrader5 as mt5
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import tti
register_matplotlib_converters()

today_AccountBalance = 0.0
spread = 0.0
pipsUpdate = ()
dailyWinLoss = ()
volume = 0.0


class trading:
    def __init__():
        pass

    def initialize():
        path = r"C:\\Program Files\\MetaTrader 5\\terminal64.exe"
        account = 510015161
        pw = "Lx4Yqo5g"
        try:
            mt5.initialize(
                path,
                login=account,
                password=pw,
                server="HantecMarkets-MT5",
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
        global spread
        try:
            ask = mt5.symbol_info_tick(symbol).ask
            bid = mt5.symbol_info_tick(symbol).bid
        except:
            return True
        # print(ask, bid)
        if type(ask) != float or type(bid) != float:
            return False
        if (ask - spread) < bid:
            return True
        else:
            return False

    def orderChecker(symbol):
        global volume
        p = mt5.positions_get(symbol=symbol)
        x = 0
        if p == () or p == None:
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

    def win_loss_Stopper():
        global today_AccountBalance
        global dailyWinLoss
        currentBalance = mt5.account_info()
        currentBalance = currentBalance[10]
        maxLoss = today_AccountBalance-dailyWinLoss[1]
        maxWin = today_AccountBalance+dailyWinLoss[0]

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

    def orderSender(symbol, t, lot, tp, sl):
        ask = mt5.symbol_info_tick(symbol).ask
        bid = mt5.symbol_info_tick(symbol).bid
        stopLoss = 0.0
        takeProfit = 0.0
        orderType = ''

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
        if result['comment'] == 'Request executed':
            print(symbol, t, result['comment'])
        else:
            return print(symbol, result['comment'], t)

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
        global pipsUpdate
        try:
            for i in orderData:
                ticker = i[0]
                t = i[5]
                stopLoss = round(i[11], 5)
                takeProfit = round(i[12], 5)
                currentPrice = i[13]
                if t == 0:
                    if pipsUpdate[0] == 0 or (currentPrice - pipsUpdate[0]) > stopLoss:
                        if pipsUpdate[2] == 0:
                            stopLoss = i[10] - .5
                        else:
                            stopLoss = currentPrice - pipsUpdate[2]
                        if pipsUpdate[1] == 0:
                            takeProfit = takeProfit - .5
                        else:
                            takeProfit = takeProfit + pipsUpdate[1]
                        key = True
                elif t == 1:
                    if pipsUpdate[0] == 0 or (currentPrice + pipsUpdate[0]) < stopLoss:
                        if pipsUpdate[2] == 0:
                            stopLoss = i[10] + .5
                        else:
                            stopLoss = currentPrice + pipsUpdate[2]
                        if pipsUpdate[1] == 0:
                            takeProfit = takeProfit - .5
                        else:
                            takeProfit = takeProfit - pipsUpdate[1]
                        key = True

                if key:
                    # print(stopLoss, takeProfit)
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

    def orderCloser(win, loss, vol):
        volume = vol
        orderData = mt5.positions_get()
        x = 0.0
        if orderData == ():
            return
        for i in orderData:
            x += i[15]
        try:
            if x > win or x < loss:
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

    def awake(spr, pips, daily, vol):
        global today_AccountBalance
        global spread
        global pipsUpdate
        global dailyWinLoss
        global volume
        spread = spr
        pipsUpdate = pips
        dailyWinLoss = daily
        volume = vol
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
        today_AccountBalance = accountBalance[10]
        trading.accountInf()
        return today_AccountBalance


if __name__ == '__main__':
    pass
