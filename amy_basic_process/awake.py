from amy_basic_process.voice_module import talkProcess as tkP
import amy_basic_process.miscellaneous as msc
from amy_basic_process.data_module import login


class awake:
    def run():
        userPrefix = login.userPrefix()
        tkP.engVoiceConfig()
        weather = msc.main.weather('Medellin')
        dateTime = msc.main.dateClock(0)
        dayPart = msc.main.dayParts()

        tkP.talk('good {}, today is {},its {}, {}'.format(
            dayPart, dateTime[1], dateTime[2], weather))
        return userPrefix


if __name__ == '__main__':
    pass
