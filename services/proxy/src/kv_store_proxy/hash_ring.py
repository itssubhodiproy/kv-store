import hashlib
from bisect import bisect_left, insort


class HashRing:
    def __init__(self, virtual_nodes: int = 100, replication_factor: int = 3):
        self.positions = []
        self.nodes = {}
        self.virtual_nodes = virtual_nodes
        self.replication_factor = replication_factor

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

    def get_nodes(self, key: str) -> list[int]:
        if self.replication_factor <= 0 or not self.positions:
            return []

        position = self._hash(key)
        index = bisect_left(self.positions, position)

        if index == len(self.positions):
            index = 0

        result = []
        seen = set()

        for offset in range(len(self.positions)):
            i = (index + offset) % len(self.positions)
            node_id = self.nodes[self.positions[i]]

            if node_id in seen:
                continue

            seen.add(node_id)
            result.append(node_id)

            if len(result) == self.replication_factor:
                break

        return result
