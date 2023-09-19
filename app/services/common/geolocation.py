
import math
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


class GeoLocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="geo_location_app")

    def get_user_ip(self):
        """
        Get the public IP address of the user.s

        Returns:
            str: The public IP address of the user.
        """
        try:
            response = requests.get("https://api.ipify.org?format=json")
            ip_data = response.json()
            return ip_data["ip"]
        except requests.exceptions.RequestException:
            return None

    def get_geolocation_data(self, ip_address=None):
        """
        Get geolocation data based on the provided IP address.

        Args:
            ip_address (str, optional): The IP address to look up. If None, the user's IP address will be used.

        Returns:
            dict: A dictionary containing geolocation data (latitude, longitude, city, country, etc.).
        """
        if not ip_address:
            ip_address = self.get_user_ip()

        try:
            url = f"https://ipinfo.io/{ip_address}/json"
            response = requests.get(url)
            geolocation_data = response.json()
            return {
                "ip": geolocation_data.get("ip"),
                "city": geolocation_data.get("city"),
                "region": geolocation_data.get("region"),
                "country": geolocation_data.get("country"),
                "latitude": geolocation_data.get("loc", "").split(",")[0],
                "longitude": geolocation_data.get("loc", "").split(",")[1],
                "timezone": geolocation_data.get("timezone"),
            }
        except requests.exceptions.RequestException:
            return None

    def calculate_distance(self, coords1, coords2):
        """
        Calculate the distance (in kilometers) between two sets of coordinates.

        Args:
            coords1 (tuple): A tuple containing the latitude and longitude of the first location.
            coords2 (tuple): A tuple containing the latitude and longitude of the second location.

        Returns:
            float: The distance between the two locations in kilometers.
        """
        return geodesic(coords1, coords2).kilometers

    def get_location_from_address(self, address):
        """
        Get geolocation data based on a given address.

        Args:
            address (str): The address to look up.

        Returns:
            dict: A dictionary containing geolocation data (latitude, longitude, city, country, etc.).
        """
        try:
            location = self.geolocator.geocode(address)
            if location:
                return {
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "city": location.raw.get("address", {}).get("city"),
                    "country": location.raw.get("address", {}).get("country"),
                }
        except Exception:
            return None

    def get_nearby_places(self, latitude, longitude, radius=500, place_type="restaurant"):
        """
        Get a list of nearby places of a specific type based on coordinates.

        Args:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.
            radius (int, optional): The search radius in meters. Default is 500 meters.
            place_type (str, optional): The type of place to search for (e.g., "restaurant", "park", "cafe", etc.).

        Returns:
            list: A list of dictionaries containing information about nearby places.
        """
        try:
            url = f"https://api.opentripmap.com/0.1/en/places/radius?radius={radius}&lon={longitude}&lat={latitude}&kinds={place_type}&format=json"
            response = requests.get(url)
            places_data = response.json()
            nearby_places = []
            for place in places_data.get("features", []):
                place_info = {
                    "name": place.get("properties", {}).get("name"),
                    "address": place.get("properties", {}).get("address"),
                    "latitude": place.get("geometry", {}).get("coordinates")[1],
                    "longitude": place.get("geometry", {}).get("coordinates")[0],
                }
                nearby_places.append(place_info)
            return nearby_places
        except requests.exceptions.RequestException:
            return []

    def reverse_geocode(self, latitude, longitude):
        """
        Perform reverse geocoding to get the address from given latitude and longitude.

        Args:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            str: The address of the given coordinates.
        """
        try:
            location = self.geolocator.reverse((latitude, longitude))
            if location:
                return location.address
        except Exception:
            return None

    def get_timezone_info(self, latitude, longitude):
        """
        Get timezone information for a specific location based on latitude and longitude.

        Args:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            dict: A dictionary containing timezone information (e.g., timezone name, UTC offset).
        """
        try:
            url = f"https://api.timezonedb.com/v2.1/get-time-zone?key=YOUR_API_KEY&format=json&by=position&lat={latitude}&lng={longitude}"
            response = requests.get(url)
            timezone_data = response.json()
            return {
                "timezone_name": timezone_data.get("zoneName"),
                "utc_offset": timezone_data.get("gmtOffset"),
            }
        except requests.exceptions.RequestException:
            return {}

    def calculate_bearing(self, coords1, coords2):
        """
        Calculate the bearing (initial compass bearing) between two sets of coordinates.

        Args:
            coords1 (tuple): A tuple containing the latitude and longitude of the first location.
            coords2 (tuple): A tuple containing the latitude and longitude of the second location.

        Returns:
            float: The bearing in degrees (0 to 360).
        """
        lat1, lon1 = coords1
        lat2, lon2 = coords2

        delta_lon = lon2 - lon1
        x = math.cos(math.radians(lat2)) * math.sin(math.radians(delta_lon))
        y = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2))) - \
            (math.sin(math.radians(lat1)) * math.cos(math.radians(lat2))
             * math.cos(math.radians(delta_lon)))

        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing
