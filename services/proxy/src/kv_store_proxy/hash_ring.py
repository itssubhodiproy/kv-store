import hashlib
from bisect import bisect_left, insort


class HashRing:
    def __init__(self, virtual_nodes: int = 100):
        self.positions = []
        self.nodes = {}
        self.virtual_nodes = virtual_nodes

    @staticmethod
    def _hash(value: str) -> int:
        digest = hashlib.md5(value.encode()).digest()
        return int.from_bytes(digest, byteorder="big")

    def add_node(self, node_id: str):
        for i in range(self.virtual_nodes):
            position = self._hash(f"{node_id}:{i}")

            if position in self.nodes:
                return

            insort(self.positions, position)
            self.nodes[position] = node_id

    def remove_node(self, node_id: str):
        for i in range(self.virtual_nodes):
            position = self._hash(f"{node_id}:{i}")

            if position not in self.nodes:
                return

            self.positions.remove(position)
            del self.nodes[position]

    def get_node(self, key: str):
        if not self.positions:
            return None

        position = self._hash(key)
        index = bisect_left(self.positions, position)

        if index == len(self.positions):
            index = 0

        return self.nodes[self.positions[index]]
