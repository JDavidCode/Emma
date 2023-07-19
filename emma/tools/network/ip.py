import sys
import socket

import requests


class ToolKit:
    def __init__():
        pass

    def get_host():
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip

    def verify_open_ports(index):
        objetive = socket.gethostbyname(index)
        print("Scanning ports")
        try:
            for port in range(1, 255):
                s = socket.socket(socket.AF_INET, socket.SOCK_SEQPACKET)
                socket.setdefaulttimeout(1)
                result = s.connect_ex((objetive, port))
                if result == 0:
                    print(f"Port {port} is open")
                s.close()
        except Exception as e:
            print(f"ERROR: \n {e}")

    def get_client_ip_addresses(request):
        # Get the client's IP addresses from the request object
        access_route = request.access_route

        # Try to find the IPv6 address from the access_route list
        ipv6_address = next((ip for ip in access_route if ":" in ip), None)

        if ipv6_address:
            # If an IPv6 address is found, return it as the local_ip
            return ipv6_address, ToolKit.get_public_ip(request=request)
        else:
            # If no IPv6 address is found, use request.remote_addr as fallback
            return request.remote_addr, ToolKit.get_public_ip(request=request)

    def get_public_ip(request=None):
        if request is None:
            # If request is None, return the server's IP address
            server_ip = socket.gethostbyname(socket.gethostname())
            return server_ip

        try:
            # Replace 'YOUR_PUBLIC_IP_SERVICE_URL' with the URL of a service that provides the public IP
            response = requests.get('https://api.ipify.org')
            if response.status_code == 200:
                return response.text.strip()
        except requests.RequestException:
            pass

        # Return None if unable to retrieve the public IP
        return None
