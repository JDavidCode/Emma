import importlib
import time
import sys
from workers.trading_bots.setup import run as run_setup


class TradingSupervisor:
    binary_market = ["EURUSD", "EURGBP", "EURJPY", "USDJPY", "AUDJPY", "GBPJPY",
                     "GBPUSD", "USDCHF", "AUDUSD", "AUDCAD", "USDCAD"]

    def __init__(self, console_output):
        sys.path.append("workers/trading_bots")
        run_setup()
        self.trading_core = importlib.import_module(
            "trading_core")
        self.IqOption(console_output, self.trading_core.tradingIqOption(console_output,
                                                                        "PRACTICE", "davidanayaacosta@hotmail.com", "Ma1040492386"))
        # self.MetaTrader5(self.trading_core.TradingMT5())

    class IqOption:
        def __init__(self, console_output, core):
            self.iq = core
            self.console_output = console_output
            self.tag = "Trading Thread | Supervisor IQ Option"
            # Bots importations
            binary_bots = importlib.import_module(
                "binariesIQ.binary_bots")
            self.binary_bots = [binary_bots.Macrsi,
                                binary_bots.Masr, binary_bots.Mrsic]

            self.run()

        def run(self):
            task_timer = [60, 120, 300]
            advisor_clock = 0
            while True:
                otc_market = False
                if self.iq.check_market("EURUSD-OTC"):
                    otc_market = True
                for i in TradingSupervisor.binary_market:
                    pair = ""
                    if otc_market:
                        pair = f"{i}-OTC"
                    else:
                        pair = i

                    if not self.iq.check_market(pair):
                        advisor_clock += 3
                        continue

                    dataset = self.iq.get_symbol_rates(pair)
                    for y in self.binary_bots:
                        signal = y.strategy(dataset)
                        if y == self.binary_bots[0]:
                            if task_timer[0] <= 60:
                                task_timer[0] += 1
                                continue
                        elif y == self.binary_bots[1]:
                            if task_timer[1] <= 300:
                                task_timer[1] += 1

                                time.sleep(.30)
                                continue
                        elif y == self.binary_bots[2]:
                            if task_timer[2] <= 540:
                                task_timer[2] += 1
                                continue

                        advisor_clock += 1
                        if signal == 0:

                            continue
                        else:
                            self.iq.order_sender(
                                pair, signal[0], signal[1])

                if (task_timer[0]-1) == 60:
                    task_timer[0] = 0
                if (task_timer[1]-1) == 120:
                    task_timer[1] = 0
                if (task_timer[2]-1) == 300:
                    task_timer[2] = 0

                if advisor_clock >= 800:
                    self.console_output.write(self.tag, "IS RUNNING")
                    advisor_clock = 0

    class MetaTrader5:
        def __init__(self, core):
            self.trading = core


if __name__ == "__main__":
    TradingSupervisor()
