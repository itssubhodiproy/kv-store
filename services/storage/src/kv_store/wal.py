import json
import os


class WAL:
    def __init__(self, data_dir="data"):
        os.makedirs(data_dir, exist_ok=True)
        self.path = os.path.join(
            data_dir,
            "wal.log",
        )

    def append(self, op, key, version, value=None):
        record = {"op": op, "key": key, "value": value, "version": version}

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
