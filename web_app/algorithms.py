def bubble_sort(items, key=None, reverse=False):
    """Сортування бульбашкою."""
    result = list(items)

    def get_value(item):
        return key(item) if key else item

    n = len(result)

    for i in range(n):
        swapped = False

        for j in range(0, n - i - 1):
            left = get_value(result[j])
            right = get_value(result[j + 1])

            if (left < right) if reverse else (left > right):
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True

        if not swapped:
            break

    return result


def quick_sort(items, key=None, reverse=False):
    """Швидке сортування."""
    result = list(items)

    def get_value(item):
        return key(item) if key else item

    def sort(values):
        if len(values) <= 1:
            return values

        pivot = get_value(values[len(values) // 2])

        left = []
        middle = []
        right = []

        for item in values:
            value = get_value(item)

            if value == pivot:
                middle.append(item)
            elif value < pivot:
                left.append(item)
            else:
                right.append(item)

        return sort(left) + middle + sort(right)

    result = sort(result)

    if reverse:
        result.reverse()

    return result


def linear_search(items, target, key=None):
    """Лінійний пошук. Повертає індекс або -1."""
    for index, item in enumerate(items):
        value = key(item) if key else item

        if value == target:
            return index

    return -1


def binary_search(items, target, key=None):
    """Бінарний пошук у відсортованому за зростанням списку."""
    left = 0
    right = len(items) - 1

    def get_value(item):
        return key(item) if key else item

    while left <= right:
        middle = (left + right) // 2
        value = get_value(items[middle])

        if value == target:
            return middle

        if value < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1
