import importlib
import multiprocessing


class TradingSupervisor:
    def __init__(self):
        TradingSupervisor.IqOption()

    class IqOption:
        def __init__(self):
            self.trading_core = importlib.import_module("trading_core")
            self.binary_macrsi = importlib.import_module(
                "binariesIQ.bot_macrsi")
            self.binary_masr = importlib.import_module("binariesIQ.bot_masr")
            self.binary_mrsic = importlib.import_module("binariesIQ.bot_mrsic")
            self.iq = self.trading_core.tradingIqOption(
                "PRACTICE", "davidanayaacosta@hotmail.com", "Ma1040492386")
            TradingSupervisor.IqOption.bot_trhead_executor(self)

        def bot_trhead_executor(self):
            processor = multiprocessing.Process()
            bot_funcs = [self.binary_macrsi.bot,
                         self.binary_masr.bot, self.binary_mrsic.bot]
            while True:
                processor = multiprocessing.Process(
                    target=TradingSupervisor.IqOption.targeting_function, args=(self.iq, bot_funcs))
                processor.start()

        def targeting_function(iq, bot_funcs):
            for func in bot_funcs:
                func(iq)

    class MetaTrader5:
        def __init__(self):
            pass


if __name__ == "__main__":
    TradingSupervisor()
