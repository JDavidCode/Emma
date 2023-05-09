import sys
import socket


class Kit:
    def __init__(self, queue_manager, console_manager):
        self.console_manager = console_manager
        self.tag = "IP TOOLS"
        self.queue = queue_manager

    def get_host(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        self.console_manager.write(
            self.tag, f"Current host: {hostname} \n Current ip: {ip}")

    def verify_open_ports(self, index):
        objetive = socket.gethostbyname(index)
        self.console_manager.write(self.tag, "Scanning ports")
        try:
            for port in range(1, 255):
                s = socket.socket(socket.AF_INET, socket.SOCK_SEQPACKET)
                socket.setdefaulttimeout(1)
                result = s.connect_ex((objetive, port))
                if result == 0:
                    self.console_manager.write(
                        self.tag, f"Port {port} is open")
                s.close()
        except Exception as e:
            self.console_manager.write(self.tag, f"ERROR: \n {e}")
