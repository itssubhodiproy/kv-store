import json
import os


class WAL:
    def __init__(self, path="data/wal.log"):
        self.path = path
        os.makedirs("data", exist_ok=True)

    def append(self, op, key, value=None):
        record = {
            "op": op,
            "key": key,
            "value": value,
        }

        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def replay(self):
        if not os.path.exists(self.path):
            return []

        records = []

        with open(self.path, "r") as f:
            for line in f:
                records.append(json.loads(line))

        return records

    def clear(self):
        open(self.path, "w").close()
