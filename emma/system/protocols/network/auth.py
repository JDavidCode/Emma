import emma.globals as EMMA_GLOBALS
import requests


class SystemNetworkAuth:
    def __init__(self, api_key):
        self.api_key = api_key

    def verify_with_server(self):
        # Replace 'main_server_url' with the actual URL of your main server
        main_server_url = 'https://api.example.com/verify'

        # Perform the verification request with the API key
        headers = {'Authorization': f'Bearer {self.api_key}'}
        try:
            response = requests.get(main_server_url, headers=headers)

            if response.status_code == 200:
                # The app is verified successfully
                return True
            else:
                # The verification failed, handle the error accordingly
                return False
        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network error)
            print(f"Error occurred during verification: {e}")
            return False
