import datetime


class MiscellaneousTask:
    def __init__(self) -> None:
        pass

    def date_clock(i):
        dateTime = datetime.datetime.now()
        clock = dateTime.time()
        date = dateTime.date()

        if i == 1:
            return dateTime.strftime("%d-%m %Y %H:%M:%S")
        elif i == 2:
            return date
        elif i == 3:
            return clock.strftime("%H:%M:%S")
        else:
            return (
                dateTime.strftime("%Y-%m-%d %H:%M:%S"),
                date,
                clock.strftime("%H:%M:%S"),
            )
