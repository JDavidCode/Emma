import datetime
import requests


class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather_data(self, city, country_code=None):
        """
        Get weather data for a specific city.

        Args:
            city (str): The name of the city.
            country_code (str, optional): The two-letter country code (ISO 3166). Default is None.

        Returns:
            dict: A dictionary containing weather data (e.g., temperature, description, humidity, etc.).
        """
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}"
            if country_code:
                url += f",{country_code}"
            url += f"&appid={self.api_key}&units=metric"
            response = requests.get(url)
            weather_data = response.json()

            if weather_data.get("cod") == 200:
                weather_info = {
                    "temperature": weather_data["main"]["temp"],
                    "description": weather_data["weather"][0]["description"],
                    "humidity": weather_data["main"]["humidity"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "icon": weather_data["weather"][0]["icon"],
                }
                return weather_info
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def get_weather_data_by_coords(self, latitude, longitude):
        """
        Get weather data for a specific location based on geographic coordinates.

        Args:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            dict: A dictionary containing weather data (e.g., temperature, description, humidity, etc.).
        """
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            weather_data = response.json()

            if weather_data.get("cod") == 200:
                weather_info = {
                    "temperature": weather_data["main"]["temp"],
                    "description": weather_data["weather"][0]["description"],
                    "humidity": weather_data["main"]["humidity"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "icon": weather_data["weather"][0]["icon"],
                }
                return weather_info
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def get_weather_forecast(self, city, country_code=None, num_days=5):
        """
        Get weather forecast for the specified number of days.

        Args:
            city (str): The name of the city.
            country_code (str, optional): The two-letter country code (ISO 3166). Default is None.
            num_days (int, optional): The number of days for the forecast. Default is 5.

        Returns:
            list: A list of dictionaries, each containing weather data for a specific day.
        """
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast/daily?q={city}"
            if country_code:
                url += f",{country_code}"
            url += f"&appid={self.api_key}&units=metric&cnt={num_days}"
            response = requests.get(url)
            forecast_data = response.json()

            if forecast_data.get("cod") == "200":
                weather_forecast = []
                for day_data in forecast_data.get("list", []):
                    weather_info = {
                        "date": datetime.fromtimestamp(day_data["dt"]),
                        "temperature": day_data["temp"]["day"],
                        "description": day_data["weather"][0]["description"],
                        "humidity": day_data["humidity"],
                        "wind_speed": day_data["speed"],
                        "icon": day_data["weather"][0]["icon"],
                    }
                    weather_forecast.append(weather_info)
                return weather_forecast
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def get_weather_data_by_zip(self, zip_code, country_code=None):
        """
        Get weather data for a specific ZIP code.

        Args:
            zip_code (str): The ZIP code.
            country_code (str, optional): The two-letter country code (ISO 3166). Default is None.

        Returns:
            dict: A dictionary containing weather data (e.g., temperature, description, humidity, etc.).
        """
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_code}"
            if country_code:
                url += f",{country_code}"
            url += f"&appid={self.api_key}&units=metric"
            response = requests.get(url)
            weather_data = response.json()

            if weather_data.get("cod") == 200:
                weather_info = {
                    "temperature": weather_data["main"]["temp"],
                    "description": weather_data["weather"][0]["description"],
                    "humidity": weather_data["main"]["humidity"],
                    "wind_speed": weather_data["wind"]["speed"],
                    "icon": weather_data["weather"][0]["icon"],
                }
                return weather_info
            else:
                return None
        except requests.exceptions.RequestException:
            return None
