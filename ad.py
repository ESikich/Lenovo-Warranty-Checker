import multiprocessing as mp
from ldap3 import Server, Connection, ALL, SUBTREE
import ldap3
from warranty_checker import process_entry
from tqdm.contrib.concurrent import process_map
from typing import Dict, Any, List, Optional

class AD:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AD object.

        Args:
            config (Dict[str, Any]): The configuration for the AD object.
        """
        self.config = config
        self.server = Server(self.config['ldap_server'], use_ssl=True, get_info=ALL)
        self.conn = None

    def connect(self):
        """
        Connect to the LDAP server.
        """
        self.conn = Connection(
            self.server,
            self.config['ad_user'],
            self.config['ad_password'],
            auto_bind=True,
            client_strategy=ldap3.RESTARTABLE
        )

    def close_connection(self):
        """
        Close the LDAP connection if it exists.
        """
        if self.conn:
            self.conn.unbind()

    def get_dev_pool(self) -> List[Optional[str]]:
        """
        Get a list of devices in the development pool.

        Returns:
            List[Optional[str]]: A list of device names in the development pool.
        """
        self.conn.search(
            search_base=self.config['search_base'],
            search_filter='(objectClass=computer)',
            attributes=['name'],
            search_scope=SUBTREE
        )

        # Process the entries in parallel
        results = process_map(
            process_entry,
            self.conn.entries,
            [self.config] * len(self.conn.entries),
            max_workers=mp.cpu_count(),
            desc='Looking for workstations'
        )

        dev_pool = []
        for result in results:
            if result is not None:
                dev_pool.append(result)

        return dev_pool
