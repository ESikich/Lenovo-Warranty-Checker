import socket

class NetUtil:

    @staticmethod
    def get_ip(hostname):
        try:
            ip_addr = socket.gethostbyname(hostname)
            return ip_addr
        except Exception as e:
            raise

    @staticmethod
    def ping(ip_addr, port=445, timeout=1):
        try:
            with socket.create_connection((ip_addr, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
