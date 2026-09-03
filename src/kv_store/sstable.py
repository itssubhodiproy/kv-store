import hashlib
import os

from .memtable import TOMBSTONE


class SSTable:
    def __init__(self, max_entries=20, max_blocks=4):
        self.max_entries = max_entries
        self.max_blocks = max_blocks

        self.next_id = self._next_sstable_id()
        self.metadata = self._load_metadata()

    # -------------------------
    # Public operations
    # -------------------------

    def flush(self, items):
        sstable_id = self.next_id

        path = f"data/sstable-{sstable_id:04d}.txt"
        index_path = f"data/sstable-{sstable_id:04d}.index"
        bloom_path = f"data/sstable-{sstable_id:04d}.bloom"

        index_entries = []
        block_size = self.max_entries // self.max_blocks
        bloom = [0] * 64

        with open(path, "w") as f, open(index_path, "w") as index:
            for i, (key, value) in enumerate(items):
                if value is TOMBSTONE:
                    value = "__TOMBSTONE__"

                self._add_to_bloom(bloom, key)

                if i % block_size == 0:
                    offset = f.tell()
                    index.write(f"{key}:{offset}\n")
                    index_entries.append((key, offset))

                f.write(f"{key}:{value}\n")

        with open(bloom_path, "w") as f:
            f.write("".join(map(str, bloom)))

        self.metadata[sstable_id] = {
            "index": index_entries,
            "bloom": bloom,
        }

        self.next_id += 1

    def get(self, key):
        for sstable_id in range(self.next_id - 1, 0, -1):
            if not self._check_bloom(sstable_id, key):
                continue

            value = self._search(sstable_id, key)

            if value == "__TOMBSTONE__":
                return TOMBSTONE

            if value is not None:
                return value

        return None

    # -------------------------
    # Search
    # -------------------------

    def _search(self, sstable_id, key):
        data_path = f"data/sstable-{sstable_id:04d}.txt"

        index = self.metadata[sstable_id]["index"]

        # Binary search sparse index
        left = 0
        right = len(index) - 1
        block = -1

        while left <= right:
            mid = (left + right) // 2

            if index[mid][0] <= key:
                block = mid
                left = mid + 1
            else:
                right = mid - 1

        if block == -1:
            return None

        start_offset = index[block][1]

        if block + 1 < len(index):
            end_offset = index[block + 1][1]
        else:
            end_offset = os.path.getsize(data_path)

        # Read only this block
        with open(data_path, "r") as f:
            f.seek(start_offset)
            data = f.read(end_offset - start_offset)

        # Small block, linear scan
        for line in data.splitlines():
            stored_key, value = line.split(":", 1)

            if stored_key == key:
                return value

        return None

    # -------------------------
    # Bloom Filter
    # -------------------------

    def _bloom_positions(self, key):
        h1 = int(hashlib.md5(key.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha1(key.encode()).hexdigest(), 16)

        return h1 % 64, h2 % 64

    def _add_to_bloom(self, bloom, key):
        for position in self._bloom_positions(key):
            bloom[position] = 1

    def _might_contain(self, key, bloom):
        for position in self._bloom_positions(key):
            if bloom[position] == 0:
                return False

        return True

    def _check_bloom(self, sstable_id, key):
        bloom = self.metadata[sstable_id]["bloom"]

        return self._might_contain(key, bloom)

    # -------------------------
    # Metadata
    # -------------------------

    def _load_metadata(self):
        metadata = {}

        for sstable_id in range(1, self.next_id):
            index_path = f"data/sstable-{sstable_id:04d}.index"
            bloom_path = f"data/sstable-{sstable_id:04d}.bloom"

            index = []

            with open(index_path, "r") as f:
                for line in f:
                    index_key, offset = line.strip().split(":")
                    index.append((index_key, int(offset)))

            with open(bloom_path, "r") as f:
                bloom = [int(bit) for bit in f.read()]

            metadata[sstable_id] = {
                "index": index,
                "bloom": bloom,
            }

        return metadata

    def _next_sstable_id(self):
        i = 1

        while os.path.exists(f"data/sstable-{i:04d}.txt"):
            i += 1

        return i
