from api.api import Paladin

def quicksort(arr):
    if len(arr) <= 1:
        return arr

    stack = [(0, len(arr) - 1)]
    while stack:
        low, high = stack.pop()
        if low < high:
            pivot_index = partition(arr, low, high)
            stack.append((low, pivot_index - 1))
            stack.append((pivot_index + 1, high))
    return arr

  
@Paladin.atomic
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


if __name__ == '__main__':
    main()
