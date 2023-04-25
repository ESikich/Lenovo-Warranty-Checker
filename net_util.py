import socket

class NetUtil:
    @staticmethod
    def get_ip(hostname: str) -> str:
        """
        Get the IP address for a given hostname.

        Args:
            hostname: A string representing the hostname to look up.

        Returns:
            A string representing the IP address associated with the hostname.

        Raises:
            Any exceptions raised by `socket.gethostbyname`.
        """
        try:
            ip_addr = socket.gethostbyname(hostname)
            return ip_addr
        except Exception as e:
            raise

    @staticmethod
    def ping(ip_addr: str, port: int = 445, timeout: int = 1) -> bool:
        """
        Check if a given IP address and port are reachable.

        Args:
            ip_addr: A string representing the IP address to check.
            port: An integer representing the port number to check. Defaults to 445.
            timeout: An integer representing the timeout value in seconds. Defaults to 1.

        Returns:
            A boolean indicating whether the IP address and port are reachable.

        Raises:
            Any exceptions raised by `socket.create_connection`.
        """
        try:
            with socket.create_connection((ip_addr, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
