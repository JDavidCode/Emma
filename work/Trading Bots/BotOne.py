from trading import *

stock = ['US100Cash']  # 'US30Cash',
balance = 0
pips = 0
vol = 0.0
volRange = {
    150.0: (18.0,  0.1),
    200.0: (21.0, 0.2),
    300.0: (22.0,  0.3),
    500.0: (21.0, 0.5),
    800.0: (22.0,  0.7),
    1000.0: (21.0, 0.9),
    1500.0: (21.0,  1.2),
    2500.0: (21.0, 1.7),
    3500.0: (21.0,  2.2),
    5000.0: (21.0, 2.8),
    10000.0: (21.0,  3.5)
}

keyUs1 = 0
keyUs3 = 0


class botCore:
    def __init__(self) -> None:
        pass

    def volumeRange():
        global balance
        global volRange
        global vol
        global pips
        x = 0.0
        for i in volRange:
            if i < balance:
                x = i
        pips = volRange[x][0]
        vol = volRange[x][1]

    def orderCheck(symbol):
        global vol
        p = mt5.positions_get(symbol=symbol)
        x = 0
        if p == () or p == None:
            return False
        elif p != () or p != None:
            for i in p:
                x += 1
        if x == 0:
            return False
        elif x > 0 and x <= 1:
            return True
        else:
            return False

    def Updater(symbol):
        try:
            orderData = mt5.positions_get(symbol=symbol)
            if orderData == ():
                return
        except:
            return
        key = False
        stopLoss = 0.0
        takeProfit = 0.0
        comparer = 00022.0
        price = 0015.0
        try:
            for i in orderData:
                ticker = i[0]
                t = i[5]
                stopLoss = round(i[11], 5)
                takeProfit = round(i[12], 5)
                currentPrice = i[13]
                if t == 0:
                    if (currentPrice - comparer) > stopLoss:
                        stopLoss = currentPrice - price
                        key = True
                elif t == 1:
                    if (currentPrice + comparer) < stopLoss:
                        stopLoss = currentPrice + price
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
            pass

    def run():
        global balance
        global keyUs1
        global keyUs3
        balance = trading.awake(0, 0, 0, 0)
        botCore.volumeRange()
        global volume
        balance = trading.awake(
            00005.0, (0, 0, 0), (400.0, 600.0), volume)
        while True:
            for i in stock:
                if trading.win_loss_Stopper() and trading.spread(i) and trading.orderChecker(i):
                    if i == 'US100Cash':
                        trading.orderSender(i, 'buy', vol, pips, (pips/3.2))
                        trading.orderSender(i, 'sell', vol, pips, (pips/3.2))
                        keyUs1 = 0
                    if i == 'US30Cash':
                        trading.orderSender(
                            i, 'buy', vol-.2, pips*1.6, (pips/1.8))
                        trading.orderSender(
                            i, 'sell', vol-.2, pips*1.6, (pips/1.8))
                        keyUs3 = 0

                if botCore.orderCheck(i):
                    if i == 'US100Cash' and keyUs1 == 0:
                        trading.orderUpdater(i)
                        keyUs1 = 1
                    if i == 'US30Cash' and keyUs3 == 0:
                        trading.orderUpdater(i)
                        keyUs3 = 1
                    if keyUs1 == 1:
                        botCore.Updater(i)
                        time.sleep(180)
                    if keyUs3 == 1:
                        botCore.Updater(i)


if __name__ == '__main__':
    botCore.run()
