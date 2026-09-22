TOMBSTONE = object()


class Node:
    def __init__(self, key, value, version):
        self.key = key
        self.value = value
        self.version = version

        self.left = None
        self.right = None
        self.height = 1


class MemTable:
    def __init__(self):
        self.root = None
        self.count = 0

    def get(self, key):
        node = self.root

        while node:
            if key == node.key:
                return node.value, node.version
            if key < node.key:
                node = node.left
            else:
                node = node.right

        return None

    def put(self, key, value, version):
        self.root = self._insert(self.root, key, value, version)

    def delete(self, key, version):
        self.root = self._insert(self.root, key, TOMBSTONE, version)

    def items(self):
        yield from self._items(self.root)

    def clear(self):
        self.root = None
        self.count = 0

    def _items(self, node):
        if not node:
            return

        yield from self._items(node.left)
        yield node.key, node.value, node.version
        yield from self._items(node.right)

    # -------------------------
    # AVL Tree
    # -------------------------

    def _insert(self, node, key, value, version):
        if not node:
            self.count += 1
            return Node(key, value, version)

        if key < node.key:
            node.left = self._insert(node.left, key, value, version)
        elif key > node.key:
            node.right = self._insert(node.right, key, value, version)
        else:
            node.value = value
            node.version = version
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
