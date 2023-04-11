import importlib
import time
import sys


class TradingSupervisor:
    euro_market = ["EURUSD", "EURGBP", "EURJPY"]
    us_market = ["USDG", "EURGBP", "EURJP"]

    def __init__(self):
        sys.path.append("workers/trading_bots")
        self.trading_core = importlib.import_module(
            "trading_core")
        self.IqOption(self.trading_core.tradingIqOption(
            "PRACTICE", "davidanayaacosta@hotmail.com", "Ma1040492386"))
        # self.MetaTrader5(self.trading_core.TradingMT5())

    class IqOption:
        def __init__(self, core):
            self.iq = core

            # Bots importations
            binary_bots = importlib.import_module(
                "binariesIQ.binary_bots")
            self.binary_bots = [binary_bots.Macrsi,
                                binary_bots.Masr, binary_bots.Mrsic]

            self.run()

        def run(self):
            while True:
                for i in TradingSupervisor.euro_market:
                    dataset = self.iq.get_symbol_rates(i)
                    for y in self.binary_bots:
                        signal = y.strategy(dataset)
                        if signal == 0:
                            continue
                        else:
                            self.iq.order_sender(
                                i, signal[0], signal[1])
                time.sleep(120)

    class MetaTrader5:
        def __init__(self, core):
            self.trading = core


if __name__ == "__main__":
    TradingSupervisor()
