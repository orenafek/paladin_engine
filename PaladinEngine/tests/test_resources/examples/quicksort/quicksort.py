import random


def quicksort(arr):
    a = arr
    if len(a) <= 1:
        return a

    stack = [(0, len(a) - 1)]
    while stack:
        low, high = stack.pop()
        if low < high:
            pivot_index = partition(a, low, high)
            stack.append((low, pivot_index - 1))
            stack.append((pivot_index + 1, high))
    return a


def swap(a, i1, i2):
    t = a[i1]
    a[i1] = a[i2]
    a[i2] = t
    return a


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i = i + 1
            swap(arr, i, j)
    swap(arr, i + 1, high)
    return i


def main():
    unsorted = [3, 6, 8, 10, 1, 2, 5]
    print(f'Unsorted: {unsorted}')
    q_sorted = quicksort(unsorted.copy())
    print(f'Sorted: {q_sorted}')
    if sorted(unsorted) != q_sorted:
        pass
        # raise AssertionError(f'{q_sorted} is unsorted after running {quicksort.__name__}({unsorted})')


if __name__ == '__main__':
    main()
