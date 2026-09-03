from .storage_engine import StorageEngine


def main():
    db = StorageEngine()

    for i in range(100):
        db.put(
            f"key-{i:03d}",
            f"value-{i}",
        )

    print(db.get("key-005"))
    print(db.get("key-055"))
    print(db.get("key-095"))
    print(db.get("does-not-exist"))


if __name__ == "__main__":
    main()
