import os

from .wal import WAL


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


TOMBSTONE = object()


class MemTable:
    def __init__(self):
        self.root = None
        self.wal = WAL()
        self.count = 0
        self.max_entries = 10
        self._recover()
        self.sstable_id = self._next_sstable_id()

    # -------------------------
    # Public operations
    # -------------------------

    def get(self, key):
        node = self.root

        while node:
            if key == node.key:
                if node.value is TOMBSTONE:
                    return None
                return node.value

            if key < node.key:
                node = node.left
            else:
                node = node.right

        return None

    def put(self, key, value):
        self.wal.append("PUT", key, value)
        self.root = self._insert(self.root, key, value)

        if self.count >= self.max_entries:
            self.flush()

    def delete(self, key):
        self.wal.append("DELETE", key)
        self.root = self._insert(self.root, key, TOMBSTONE)

        if self.count >= self.max_entries:
            self.flush()

    # -------------------------
    # Flush / Recovery
    # -------------------------

    def flush(self):
        path = f"data/sstable-{self.sstable_id:04d}.txt"

        with open(path, "w") as f:
            for key, value in self._items(self.root):
                if value is TOMBSTONE:
                    value = "__TOMBSTONE__"

                f.write(f"{key}:{value}\n")

        self.wal.clear()

        self.sstable_id += 1
        self.root = None
        self.count = 0

    def _recover(self):
        for record in self.wal.replay():
            if record["op"] == "PUT":
                self.root = self._insert(
                    self.root,
                    record["key"],
                    record["value"],
                )

            elif record["op"] == "DELETE":
                self.root = self._insert(
                    self.root,
                    record["key"],
                    TOMBSTONE,
                )

    def _items(self, node):
        if not node:
            return

        yield from self._items(node.left)
        yield node.key, node.value
        yield from self._items(node.right)

    def _next_sstable_id(self):
        i = 1

        while os.path.exists(f"data/sstable-{i:04d}.txt"):
            i += 1

        return i

    # -------------------------
    # AVL Tree
    # -------------------------

    def _insert(self, node, key, value):
        if not node:
            self.count += 1
            return Node(key, value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node

        node.height = 1 + max(
            self._height(node.left),
            self._height(node.right),
        )

        balance = self._balance(node)

        # Left heavy
        if balance > 1:
            if key > node.left.key:
                node.left = self._rotate_left(node.left)

            return self._rotate_right(node)

        # Right heavy
        if balance < -1:
            if key < node.right.key:
                node.right = self._rotate_right(node.right)

            return self._rotate_left(node)

        return node

    def _height(self, node):
        return node.height if node else 0

    def _balance(self, node):
        return self._height(node.left) - self._height(node.right)

    def _rotate_left(self, node):
        new_root = node.right
        child = new_root.left

        new_root.left = node
        node.right = child

        node.height = 1 + max(
            self._height(node.left),
            self._height(node.right),
        )

        new_root.height = 1 + max(
            self._height(new_root.left),
            self._height(new_root.right),
        )

        return new_root

    def _rotate_right(self, node):
        new_root = node.left
        child = new_root.right

        new_root.right = node
        node.left = child

        node.height = 1 + max(
            self._height(node.left),
            self._height(node.right),
        )

        new_root.height = 1 + max(
            self._height(new_root.left),
            self._height(new_root.right),
        )

        return new_root
