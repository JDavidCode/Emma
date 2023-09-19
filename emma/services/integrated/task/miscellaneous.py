import datetime


class MiscellaneousTask:
    def __init__(self) -> None:
        pass

    def date_clock(self, i):
        dateTime = datetime.datetime.now()
        clock = dateTime.time()
        date = dateTime.date()

        if i == 1:
            return True, str(dateTime.strftime("%d-%m %Y %H:%M:%S"))
        elif i == 2:
            return True, str(date)
        elif i == 3:
            return True, str(clock.strftime("%H:%M:%S"))
        else:
            return True, (
                dateTime.strftime("%Y-%m-%d %H:%M:%S"),
                date,
                clock.strftime("%H:%M:%S"),
            )
        
    def convert_currency(self, amount, from_currency, to_currency):
        # Implement the logic to use a currency exchange API to perform the conversion
        # and return the converted amount
        conversion_rate = 0.85  # Dummy conversion rate for demonstration purposes
        converted_amount = amount * conversion_rate
        return True, converted_amount