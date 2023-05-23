import subprocess


class NetworkPolicyEnforcer:
    def __init__(self):
        pass

    def allow_traffic(self, source_ip, destination_ip, port):
        self._run_iptables_command(
            [
                "INPUT",
                "-s",
                source_ip,
                "-d",
                destination_ip,
                "-p",
                "tcp",
                "--dport",
                str(port),
                "-j",
                "ACCEPT",
            ]
        )
        self._run_iptables_command(
            [
                "OUTPUT",
                "-s",
                destination_ip,
                "-d",
                source_ip,
                "-p",
                "tcp",
                "--sport",
                str(port),
                "-j",
                "ACCEPT",
            ]
        )

    def deny_traffic(self, source_ip, destination_ip, port):
        self._run_iptables_command(
            [
                "INPUT",
                "-s",
                source_ip,
                "-d",
                destination_ip,
                "-p",
                "tcp",
                "--dport",
                str(port),
                "-j",
                "DROP",
            ]
        )
        self._run_iptables_command(
            [
                "OUTPUT",
                "-s",
                destination_ip,
                "-d",
                source_ip,
                "-p",
                "tcp",
                "--sport",
                str(port),
                "-j",
                "DROP",
            ]
        )

    def apply_acl(self, source_ip, destination_ip):
        self._run_iptables_command(
            ["INPUT", "-s", source_ip, "-d", destination_ip, "-j", "DROP"])
        self._run_iptables_command(
            ["OUTPUT", "-s", destination_ip, "-d", source_ip, "-j", "DROP"])

    def enable_deny_all(self):
        self._run_iptables_command(["INPUT", "-P", "DROP"])
        self._run_iptables_command(["OUTPUT", "-P", "DROP"])
        self._run_iptables_command(["FORWARD", "-P", "DROP"])

    def disable_deny_all(self):
        self._run_iptables_command(["INPUT", "-P", "ACCEPT"])
        self._run_iptables_command(["OUTPUT", "-P", "ACCEPT"])
        self._run_iptables_command(["FORWARD", "-P", "ACCEPT"])

    def apply_rate_limit(self, interface, limit):
        subprocess.run(
            ["tc", "qdisc", "add", "dev", interface, "root",
                "tbf", "rate", limit, "burst", "10kb"]
        )

    def remove_rate_limit(self, interface):
        subprocess.run(["tc", "qdisc", "del", "dev", interface, "root"])

    def apply_segmentation(self, source_subnet, destination_subnet):
        self._run_iptables_command(
            ["FORWARD", "-s", source_subnet, "-d",
                destination_subnet, "-j", "ACCEPT"]
        )
        self._run_iptables_command(
            ["FORWARD", "-s", destination_subnet,
                "-d", source_subnet, "-j", "ACCEPT"]
        )
        self._run_iptables_command(["FORWARD", "-j", "DROP"])

    def _run_iptables_command(self, args):
        command = ["iptables"] + args
        subprocess.run(command)


    class FirewallPolicyEnforcer:
        def __init__(self):
            pass

        def allow_traffic(self, port, protocol="tcp"):
            subprocess.run(["ufw", "allow", str(port) + "/" + protocol])

        def deny_traffic(self, port, protocol="tcp"):
            subprocess.run(["ufw", "deny", str(port) + "/" + protocol])

        def enable_firewall(self):
            subprocess.run(["ufw", "enable"])

        def disable_firewall(self):
            subprocess.run(["ufw", "disable"])

        def show_rules(self):
            subprocess.run(["ufw", "status"])

        def enable_logging(self):
            subprocess.run(["ufw", "logging", "on"])

        def disable_logging(self):
            subprocess.run(["ufw", "logging", "off"])
