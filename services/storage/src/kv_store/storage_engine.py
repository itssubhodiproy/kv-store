from .memtable import MemTable
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
        result = self.memtable.get(key)

        if result is not None:
            return result

        return self.sstable.get(key)

    def put(self, key, value, version):
        self.wal.append("PUT", key, version, value)
        self.memtable.put(key, value, version)

        if self.memtable.count >= self.max_entries:
            self._flush()

    def delete(self, key, version):
        self.wal.append("DELETE", key, version=version)
        self.memtable.delete(key, version)

        if self.memtable.count >= self.max_entries:
            self._flush()

    def _flush(self):
        self.sstable.flush(self.memtable.items())

        self.wal.clear()
        self.memtable.clear()

    def _recover(self):
        for record in self.wal.replay():
            if record["op"] == "PUT":
                self.memtable.put(record["key"], record["value"], record["version"])

            elif record["op"] == "DELETE":
                self.memtable.delete(record["key"], record["version"])
