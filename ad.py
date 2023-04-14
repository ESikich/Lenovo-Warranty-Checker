import multiprocessing as mp
from ldap3 import Server, Connection, ALL, SUBTREE
import ldap3
from warranty_checker import process_entry
from tqdm.contrib.concurrent import process_map

class AD:
    def __init__(self, config):
        self.config = config
        self.server = Server(self.config['ldap_server'], use_ssl=True, get_info=ALL)
        self.conn = None

    def connect(self):
        self.conn = Connection(self.server, self.config['ad_user'], self.config['ad_password'], auto_bind=True, client_strategy=ldap3.RESTARTABLE)

    def close_connection(self):
        if self.conn:
            self.conn.unbind()

    def get_dev_pool(self):
        self.conn.search(search_base=self.config['search_base'], search_filter='(objectClass=computer)', attributes=['name'], search_scope=SUBTREE)

        results = process_map(process_entry, self.conn.entries, [self.config] * len(self.conn.entries), max_workers=mp.cpu_count(), desc='Processing device pool')

        dev_pool = []
        for result in results:
            if result is not None:
                dev_pool.append(result)

        return dev_pool
