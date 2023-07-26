import datetime


class TimeService:
    def __init__(self):
        pass

    def is_future_datetime(self, target_time):
        """
        Check if a datetime object is in the future.

        Args:
            target_time (datetime): The datetime object to check.

        Returns:
            bool: True if the target time is in the future, False otherwise.
        """
        return target_time > datetime.now()

    def calculate_time_duration(self, start_time, end_time):
        """
        Calculate the time duration between two datetime objects.

        Args:
            start_time (datetime): The starting datetime object.
            end_time (datetime): The ending datetime object.

        Returns:
            timedelta: The time duration as a timedelta object.
        """
        return end_time - start_time

    def to_utc_timestamp(self, dt):
        """
        Convert a datetime object to a UTC timestamp.

        Args:
            dt (datetime): The datetime object.

        Returns:
            int: The UTC timestamp corresponding to the datetime object.
        """
        return int(dt.timestamp())

    def get_current_utc_time(self):
        """
        Get the current UTC time.

        Returns:
            datetime: The current datetime object in UTC.
        """
        return datetime.now(datetime.timezone.utc)

    def get_current_time(self, timezone_name=None):
        """
        Get the current time.

        Args:
            timezone_name (str, optional): The name of the timezone. If None, the system's local timezone will be used.

        Returns:
            datetime: The current datetime object in the specified timezone.
        """
        if timezone_name:
            return datetime.now(datetime.timezone.utc).astimezone(datetime.timezone.timezone(timezone_name))
        else:
            return datetime.now()

    def add_hours_to_time(self, time, hours):
        """
        Add a specified number of hours to a given time.

        Args:
            time (datetime): The initial datetime object.
            hours (int): The number of hours to add.

        Returns:
            datetime: The updated datetime object with the added hours.
        """
        return time + datetime.timedelta(hours=hours)

    def is_time_within_range(self, target_time, start_time, end_time):
        """
        Check if a target time is within a given time range.

        Args:
            target_time (datetime): The target time to check.
            start_time (datetime): The start time of the range.
            end_time (datetime): The end time of the range.

        Returns:
            bool: True if the target time is within the range, False otherwise.
        """
        return start_time <= target_time <= end_time

    def from_utc_timestamp(self, timestamp):
        """
        Convert a UTC timestamp to a datetime object.

        Args:
            timestamp (int): The UTC timestamp.

        Returns:
            datetime: The datetime object corresponding to the UTC timestamp.
        """
        return datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)

    def time_difference(self, start_time, end_time):
        """
        Calculate the time difference between two datetime objects.

        Args:
            start_time (datetime): The starting datetime object.
            end_time (datetime): The ending datetime object.

        Returns:
            timedelta: The time difference as a timedelta object.
        """
        return end_time - start_time
