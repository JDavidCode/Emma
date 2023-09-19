import datetime


class TimeService:
    def __init__(self):
        pass

    def is_future_datetime(self, target_time):
        return target_time > datetime.now()

    def calculate_time_duration(self, start_time, end_time):
        return end_time - start_time

    def to_utc_timestamp(self, dt):
        return int(dt.timestamp())

    def get_current_utc_time(self):
        return datetime.now(datetime.timezone.utc)

    def get_current_time(self, timezone_name=None):
        if timezone_name:
            return datetime.now(datetime.timezone.utc).astimezone(datetime.timezone.timezone(timezone_name))
        else:
            return datetime.now()

    def add_hours_to_time(self, time, hours):
        return time + datetime.timedelta(hours=hours)

    def is_time_within_range(self, target_time, start_time, end_time):
        return start_time <= target_time <= end_time

    def from_utc_timestamp(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)

    def time_difference(self, start_time, end_time):
        return end_time - start_time
