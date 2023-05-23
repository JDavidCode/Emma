class IntrusionDetectionSystem:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def detect_intrusion(self, packet):
        for rule in self.rules:
            if rule.matches(packet):
                return True
        return False


class Rule:
    def __init__(self, source_ip, destination_ip, port):
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.port = port

    def matches(self, packet):
        return (
            packet.source_ip == self.source_ip
            and packet.destination_ip == self.destination_ip
            and packet.port == self.port
        )


class Packet:
    def __init__(self, source_ip, destination_ip, port):
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.port = port