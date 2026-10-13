from collections import deque


class FIFOQueue:
    """Черга FIFO: першим виходить перший доданий елемент."""

    def __init__(self):
        self._items = deque()

    def enqueue(self, item):
        """Додає елемент у кінець черги."""
        self._items.append(item)

    def dequeue(self):
        """Видаляє та повертає перший елемент черги."""
        if self.is_empty():
            raise IndexError("Черга порожня")

        return self._items.popleft()

    def is_empty(self):
        """Перевіряє, чи порожня черга."""
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)


class LIFOStack:
    """Стек LIFO: останнім доданий елемент виходить першим."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Додає елемент на вершину стека."""
        self._items.append(item)

    def pop(self):
        """Видаляє та повертає верхній елемент стека."""
        if self.is_empty():
            raise IndexError("Стек порожній")

        return self._items.pop()

    def is_empty(self):
        """Перевіряє, чи порожній стек."""
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)
