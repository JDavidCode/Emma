

import random
import re
import webbrowser
from bs4 import BeautifulSoup
import requests


class WebTask:
    def __init__(self):
        pass

    def google_search(self, query):
        link = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return True, link

    def youtube_search(self, query):
        link = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return True, link

    def open_webpage(self, page):
        url=page
        #index btw pages and return url
        return True, url

    def generate_link(self, protocol, domain, path=""):
        link = f"{protocol}://{domain}/{path}" if path else f"{protocol}://{domain}"
        return True, link

    def shorten_link(self, long_url):
        shortened_url = "https://short.link/abc123"
        return True, shortened_url

    def screenshot_webpage(self, url, save_path):
        screenshot_path = "/path/to/screenshot.png"
        return True, screenshot_path

    def extract_links_from_webpage(self, url):
        try:
            response = requests.get(url)
            links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
            return True, links
        except requests.exceptions.RequestException:
            return False, []

    def download_file(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True, save_path
        except requests.exceptions.RequestException:
            return False, None

    def get_website_title(self, url):
        try:
            response = requests.get(url)
            pattern = r'<title[^>]*>([^<]+)</title>'
            match = re.search(pattern, response.text, re.IGNORECASE)
            if match:
                return True, match.group(1)
            else:
                return True, None
        except requests.exceptions.RequestException:
            return False, None

    def check_website_status(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True, "Website is online."
            else:
                return True, f"Website is online, but returned status code: {response.status_code}"
        except requests.exceptions.RequestException:
            return True, "Website is unreachable or offline."

    def search_images_google(self, query):
        try:
            search_url = f"https://www.google.com/search?tbm=isch&q={query.replace(' ', '+')}"
            response = requests.get(search_url)
            links = re.findall(r'imgurl=([^&]+)', response.text)
            return True, links
        except requests.exceptions.RequestException:
            return False, []

    def check_domain_availability(self, domain):
        # Implement the logic to check the domain's availability using a domain registrar API
        # or by performing DNS queries
        is_available = random.choice([True, False])
        if is_available:
            return True, f"The domain {domain} is available."
        else:
            return True, f"The domain {domain} is not available."

    def get_webpage_headers(self, url):
        try:
            response = requests.head(url)
            headers = response.headers
            return True, headers
        except requests.exceptions.RequestException:
            return False, {}

    def generate_qr_code(self, data, size=200):
        qr_code_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xc8'
        return True, qr_code_data

    def scrape_webpage(self, url, element="p"):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            scraped_content = [tag.get_text()
                               for tag in soup.find_all(element)]
            return True, scraped_content
        except requests.exceptions.RequestException:
            return False, []

    def convert_currency(self, amount, from_currency, to_currency):
        # Implement the logic to use a currency exchange API to perform the conversion
        # and return the converted amount
        conversion_rate = 0.85  # Dummy conversion rate for demonstration purposes
        converted_amount = amount * conversion_rate
        return True, converted_amount

    def check_website_security(self, url):
        # Implement the logic to check the SSL/TLS certificate of the website
        # and verify its security level (e.g., valid, expired, self-signed, etc.)
        security_status = "Valid SSL certificate"
        return True, security_status
