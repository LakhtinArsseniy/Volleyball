import pytest

from web_app.structures import FIFOQueue, LIFOStack


def test_fifo_order():
    queue = FIFOQueue()
    queue.enqueue("A")
    queue.enqueue("B")
    queue.enqueue("C")

    assert queue.dequeue() == "A"
    assert queue.dequeue() == "B"
    assert queue.dequeue() == "C"
    assert queue.is_empty()


def test_fifo_empty():
    queue = FIFOQueue()

    with pytest.raises(IndexError):
        queue.dequeue()


def test_lifo_order():
    stack = LIFOStack()
    stack.push("A")
    stack.push("B")
    stack.push("C")

    assert stack.pop() == "C"
    assert stack.pop() == "B"
    assert stack.pop() == "A"
    assert stack.is_empty()


def test_lifo_empty():
    stack = LIFOStack()

    with pytest.raises(IndexError):
        stack.pop()