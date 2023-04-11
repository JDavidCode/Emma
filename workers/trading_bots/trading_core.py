import datetime
import importlib
import pytz
import time
import MetaTrader5 as mt5
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from iqoptionapi.stable_api import IQ_Option
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import talib as ti
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

today_AccountBalance = 0.0
dailyWinLoss = ()


class TradingMT5:
    def __init__(self, daily):
        global today_AccountBalance
        global dailyWinLoss
        dailyWinLoss = daily

        self.initializeMT()
        symbols = mt5.symbols_get()

        count = 0
        # display the first five ones
        for s in symbols:
            count += 1
            print("{}. {}".format(count, s.name))
            if count == 75:
                break
        print()
        today_AccountBalance = mt5.account_info()[10]
        print(today_AccountBalance)
        self.accountInf()

    def initializeMT():
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

    def account_info():
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

    def total_orders():
        orders = mt5.orders_total()
        print('Total Orders:', orders)
        return

    def terminal_info():
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

    def get_symbol(index):
        symbol = mt5.symbols_get("*{}*".format(index))
        print('Found symbols: ', len(symbol))
        for s in symbol:
            print(s.name)

    def spread(symbol):
        try:
            ask = mt5.symbol_info_tick(symbol).ask
            bid = mt5.symbol_info_tick(symbol).bid
        except:
            return True
        # print(ask, bid)
        if type(ask) != float or type(bid) != float:
            return False
        if (ask - 4.0) < bid:
            return True
        else:
            return False

    def order_checker(symbol, _id):
        p = mt5.positions_get(symbol=symbol)
        if p == () or p == None:
            return True
        elif p != ():
            for i in p:
                if i[18] == _id:
                    return False
                else:
                    return True
        else:
            return False

    def get_symbol_rates(symbol, count, time):
        rates = mt5.copy_rates_from_pos(
            symbol,
            time,
            0,
            count)
        rates = pd.DataFrame(rates)
        rates['time'] = pd.to_datetime(rates['time'], unit='s')
        rates['DateTime'] = pd.DatetimeIndex(
            pd.to_datetime(rates['time'], unit='s'))
        rates = rates.set_index('DateTime')
        rates.rename(columns={'open': 'Open', 'high': 'High',
                     'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
        return rates

    def entry_break(symbol, m, s):
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

    def time_schedule():
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

    def show_graphichs(rates, n, plots_order):
        fig, axe = plt.subplots(n, 1)
        x = 0
        for i in plots_order:
            axe[x].plot(rates[i])
            axe[x].set_title(i)
            # axe[x].axhline(y=0, color='b', linewidth=1)
            x += 1
        plt.tight_layout()
        fig.autofmt_xdate()
        plt.show()

    def order_sender(symbol, t, lot, tp, sl, _id):
        ask = mt5.symbol_info_tick(symbol).ask
        stopLoss = 0.0
        takeProfit = 0.0
        orderType = ''

        if t == '':
            return

        if t == 'buy':
            orderType = mt5.ORDER_TYPE_BUY
            stopLoss = ask * sl
            takeProfit = ask * tp
        elif t == 'sell':
            orderType = mt5.ORDER_TYPE_SELL
            stopLoss = ask * sl
            takeProfit = ask * tp

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": orderType,
            "price": ask,
            "sl": stopLoss,
            "tp": takeProfit,
            "deviation": 20,
            "slippage": 2,
            "magic": _id,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        result = mt5.order_send(request)
        result = result._asdict()
        if result['comment'] == 'Request executed':
            print(symbol, t, result['comment'])
        else:
            return print(symbol, result['comment'], t)

    def order_updater(symbol):
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

    def order_closer(win, loss, vol, _id):
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
                            "magic": _id,
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


class tradingIqOption():
    tradingOTC = False
    stockOpen = True
    iqoption = None

    def __init__(self, MODE, account, pw):
        self.iqoption = IQ_Option(account, pw)
        sys = importlib.import_module('amy_basic_process.sys_v')
        self.console_output = sys.ThreadManager.ConsoleOutput()
        self.check, self.reason = self.iqoption.connect()
        if self.check:
            self.console_output.write("Connect Successfully")
        else:
            self.console_output.write("connect Failure")
        tradingIqOption.iqoption = self.iqoption
        self.iqoption.change_balance(MODE)  # MODE: "PRACTICE"/"REAL"

    def initializeIQ(self):
        error_password = """{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""
        if self.check:
            self.console_output.write("Conection successfully")
            # if see this you can close network for test
            if self.iqoption.check_connect() == False:  # detect the websocket is close
                self.console_output.write("try reconnect")
                check, reason = self.iqoption.connect()
                if check:
                    self.console_output.write("Reconnect successfully")
                else:
                    if reason == error_password:
                        self.console_output.write("Error Password")
                    else:
                        self.console_output.write("No Network")

        else:
            if reason == "[Errno -2] Name or service not known":
                self.console_output.write("No Network")
            elif reason == error_password:
                self.console_output.write("Error Password")

    def account_info(self):
        self.console_output.write(
            f"Account Balance ${self.iqoption.get_balance()} {self.iqoption.get_currency()}")

    def check_open_asset(self):
        ALL_Asset = self.iqoption.get_all_open_time()
        if (ALL_Asset["digital"]["EURUSD-OTC"]["open"]):
            self.tradingOTC = True
            self.console_output.write("OTC trading asset is open")
        elif (ALL_Asset["digital"]["EURUSD"]["open"]):
            self.tradingOTC = False
            self.console_output.write("Normal trading asset is open")
        else:
            self.stockOpen = False

    def get_symbol_rates(self, symbol):
        rates = self.iqoption.get_candles(symbol, 60, 180, time.time())

        rates = pd.DataFrame(rates)
        rates['time'] = pd.to_datetime(rates['from'], unit='s')
        rates['DateTime'] = pd.DatetimeIndex(
            pd.to_datetime(rates['time'], unit='s'))
        rates = rates.set_index('DateTime')
        rates.drop(rates.columns[[0, 1, 2, 3]], axis=1, inplace=True)
        rates.rename(columns={'open': 'Open', 'max': 'High',
                     'min': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        rates = rates[["time", "Open", "High", "Low", "Close", "Volume"]]
        return rates

    def loss_stopper(self):
        data = self.iqoption.get_optioninfo(3)
        data = data["msg"]["result"]["closed_options"]
        strike = 0
        for i in data:
            last_result = i['win']
            if last_result == 'loose':
                strike += 1
        if strike >= 2:
            return False
        else:
            return True

    def order_sender(self, symbol, action, expiration):
        check, _id = self.iqoption.buy(10, symbol, action, expiration)
        if check:
            self.console_output.write(f"¡{symbol} {action} {expiration}!")
        else:
            self.console_output.write(f"¡{symbol} {action} {expiration} fail!")


class InvestingNews:
    def __init__(self):
        InvestingNews.invest_lock()

    def invest_lock():
        pass  # NEED TO SEARCH AN APPROPIATE FREE API


if __name__ == '__main__':
    InvestingNews()
