# Auto-generated Code Vault for 'ConsistentHashingRing' [Python]

import hashlib
import bisect

class ConsistentHashingRing:
    def __init__(self, num_virtual_nodes=100):
        self.num_virtual_nodes = num_virtual_nodes
        self.ring = {}
        self.sorted_keys = []

    def add_server(self, server_name):
        for i in range(self.num_virtual_nodes):
            key = f"{server_name}-{i}"
            hash_key = self._hash(key)
            if hash_key not in self.ring:
                self.ring[hash_key] = server_name
                bisect.insort(self.sorted_keys, hash_key)

    def remove_server(self, server_name):
        for i in range(self.num_virtual_nodes):
            key = f"{server_name}-{i}"
            hash_key = self._hash(key)
            if hash_key in self.ring:
                del self.ring[hash_key]
                self.sorted_keys.remove(hash_key)

    def get_server(self, key):
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            return self.ring[self.sorted_keys[0]]
        else:
            return self.ring[self.sorted_keys[idx]]

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

def main():
    ring = ConsistentHashingRing()
    servers = ['Server A', 'Server B', 'Server C']
    for server in servers:
        ring.add_server(server)

    data_keys = ['key1', 'key2', 'key3', 'key4', 'key5']
    print("Initial Distribution:")
    for key in data_keys:
        server = ring.get_server(key)
        print(f"Key '{key}' goes to {server}")

    ring.remove_server('Server B')
    print("\nDistribution after removing 'Server B':")
    for key in data_keys:
        server = ring.get_server(key)
        print(f"Key '{key}' goes to {server}")

if __name__ == "__main__":
    main()
