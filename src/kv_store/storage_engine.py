from .memtable import TOMBSTONE, MemTable
from .sstable import SSTable
from .wal import WAL


class StorageEngine:
    def __init__(self, data_dir="data"):
        self.max_entries = 20

        self.memtable = MemTable()
        self.wal = WAL(data_dir=data_dir)
        self.sstable = SSTable(
            data_dir=data_dir,
            max_entries=self.max_entries,
            max_blocks=4,
        )

        self._recover()

    def get(self, key):
        value = self.memtable.get(key)

        if value is TOMBSTONE:
            return None

        if value is not None:
            return value

        value = self.sstable.get(key)

        if value is TOMBSTONE:
            return None

        return value

    def put(self, key, value):
        self.wal.append("PUT", key, value)
        self.memtable.put(key, value)

        if self.memtable.count >= self.max_entries:
            self._flush()

    def delete(self, key):
        self.wal.append("DELETE", key)
        self.memtable.delete(key)

        if self.memtable.count >= self.max_entries:
            self._flush()

    def _flush(self):
        self.sstable.flush(self.memtable.items())

        self.wal.clear()
        self.memtable.clear()

    def _recover(self):
        for record in self.wal.replay():
            if record["op"] == "PUT":
                self.memtable.put(
                    record["key"],
                    record["value"],
                )

            elif record["op"] == "DELETE":
                self.memtable.delete(record["key"])
