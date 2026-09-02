from .memtable import MemTable


def main():
    memtable = MemTable()

    for i in range(100):
        memtable.put(f"key-{i}", f"value-{i}")


if __name__ == "__main__":
    main()
