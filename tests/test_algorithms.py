import pytest

from web_app.algorithms import (
    bubble_sort,
    quick_sort,
    linear_search,
    binary_search,
)


@pytest.mark.parametrize(
    "items, expected",
    [
        ([5, 2, 8, 1, 3], [1, 2, 3, 5, 8]),
        ([], []),
        ([1], [1]),
        ([4, 2, 2, 1], [1, 2, 2, 4]),
    ],
)
def test_bubble_sort(items, expected):
    assert bubble_sort(items) == expected


def test_bubble_sort_reverse():
    assert bubble_sort([5, 2, 8, 1], reverse=True) == [8, 5, 2, 1]


def test_quick_sort():
    assert quick_sort([5, 2, 8, 1, 3]) == [1, 2, 3, 5, 8]


def test_quick_sort_with_duplicates():
    assert quick_sort([4, 2, 2, 1, 4]) == [1, 2, 2, 4, 4]


def test_quick_sort_reverse():
    assert quick_sort([5, 2, 8, 1], reverse=True) == [8, 5, 2, 1]


def test_linear_search_found():
    assert linear_search([5, 2, 8, 1, 3], 8) == 2


def test_linear_search_not_found():
    assert linear_search([5, 2, 8, 1, 3], 10) == -1


def test_binary_search_found():
    assert binary_search([1, 2, 3, 5, 8], 5) == 3


def test_binary_search_not_found():
    assert binary_search([1, 2, 3, 5, 8], 7) == -1


def test_binary_search_empty():
    assert binary_search([], 5) == -1


def test_sort_does_not_change_original_list():
    items = [5, 2, 8, 1]

    bubble_sort(items)
    quick_sort(items)

    assert items == [5, 2, 8, 1]
