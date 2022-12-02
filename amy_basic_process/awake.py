from amy_basic_process.voice_module import talkProcess as tkP
from amy_basic_process.sys import backgroundProcess as sys
import amy_basic_process.miscellaneous as msc


class awake:
    def run():
        tkP.engVoiceConfig()
        sys.moduleReloader("amy_basic_process.data_module")
        weather = msc.main.weather('Medellin')
        dateTime = msc.main.dateClock(0)
        dayPart = msc.main.dayParts()

        tkP.talk('good {}, today is {},its {}, {}'.format(
            dayPart, dateTime[1], dateTime[2], weather))
        return


if __name__ == '__main__':
    pass
