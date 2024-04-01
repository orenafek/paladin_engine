from stubs.stubs import __AC__, __ARG__, __AS__, __BMFCS__, __BREAK__, __DEF__, __EOLI__, __FC__, __FLI__, __FRAME__, __IS_STUBBED__, __PAUSE__, __PIS__, __PRINT__, __RESUME__, __SOL__, __SOLI__, __UNDEF__


from api.api import Paladin

def quicksort(arr):
    __DEF__('quicksort', line_no=3, frame=__FRAME__())
    __ARG__('quicksort', __FRAME__(), 3, arr=arr)
    if __FC__('len(arr)', len, locals(), globals(), __FRAME__(), 4, arr) <= 1:
        __UNDEF__('quicksort', __FRAME__(), 5)
        return arr
    stack = [(0, __FC__('len(arr)', len, locals(), globals(), __FRAME__(), 7, arr) - 1)]
    __AS__('stack = [(0, __FC__(@len(arr)@, len, locals(), globals(), __FRAME__(), 7, arr) - 1)]', 'stack', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=7)
    __SOL__(__FRAME__(), 8)
    while stack:
        __SOLI__(8, __FRAME__())
        (low, high) = __BMFCS__(__FC__('stack.pop()', stack.pop, locals(), globals(), __FRAME__(), 9), stack, 'stack', 'pop', 9, __FRAME__(), locals(), globals())
        __AS__('(low, high) = __BMFCS__(__FC__(@stack.pop()@, stack.pop, locals(), globals(), __FRAME__(), 9), stack, @stack@, @pop@, 9, __FRAME__(), locals(), globals())', 'high', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=9)
        __AS__('(low, high) = __BMFCS__(__FC__(@stack.pop()@, stack.pop, locals(), globals(), __FRAME__(), 9), stack, @stack@, @pop@, 9, __FRAME__(), locals(), globals())', 'low', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=9)
        if low < high:
            pivot_index = __FC__('partition(arr, low, high)', partition, locals(), globals(), __FRAME__(), 11, arr, low, high)
            __AS__('pivot_index = __FC__(@partition(arr, low, high)@, partition, locals(), globals(), __FRAME__(), 11, arr, low, high)', 'pivot_index', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=11)
            __BMFCS__(__FC__('stack.append((low, pivot_index - 1))', stack.append, locals(), globals(), __FRAME__(), 12, (low, pivot_index - 1)), stack, 'stack', 'append', 12, __FRAME__(), locals(), globals(), (low, pivot_index - 1))
            __BMFCS__(__FC__('stack.append((pivot_index + 1, high))', stack.append, locals(), globals(), __FRAME__(), 13, (pivot_index + 1, high)), stack, 'stack', 'append', 13, __FRAME__(), locals(), globals(), (pivot_index + 1, high))
        __EOLI__(__FRAME__(), loop_start_line_no=8, loop_end_line_no=13)
    __UNDEF__('quicksort', __FRAME__(), 14)
    return arr

@Paladin.atomic
def swap(a, i1, i2):
    __DEF__('swap', line_no=18, frame=__FRAME__())
    __PAUSE__()
    __ARG__('swap', __FRAME__(), 18, a=a, i1=i1, i2=i2)
    t = a[i1]
    __AS__('t = a[i1]', 't', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=19)
    a[i1] = a[i2]
    __AS__('a[i1] = a[i2]', 'a[i1]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=20)
    a[i2] = t
    __AS__('a[i2] = t', 'a[i2]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=21)
    __RESUME__()
    __UNDEF__('swap', __FRAME__(), 22)
    return a

def partition(arr, low, high):
    __DEF__('partition', line_no=25, frame=__FRAME__())
    __ARG__('partition', __FRAME__(), 25, arr=arr, low=low, high=high)
    pivot = arr[high]
    __AS__('pivot = arr[high]', 'pivot', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=26)
    i = low - 1
    __AS__('i = low - 1', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=27)
    __SOL__(__FRAME__(), 28)
    for __iter_0 in __FC__('range(low, high)', range, locals(), globals(), __FRAME__(), 28, low, high):
        __SOLI__(28, __FRAME__())
        j = __iter_0
        __AS__('j = __iter_0', 'j', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=28)
        if arr[j] <= pivot:
            i = i + 1
            __AS__('i = i + 1', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=30)
            __FC__('swap(arr, i, j)', swap, locals(), globals(), __FRAME__(), 31, arr, i, j)
        __EOLI__(__FRAME__(), loop_start_line_no=28, loop_end_line_no=31)
    __FC__('swap(arr, i + 1, high)', swap, locals(), globals(), __FRAME__(), 32, arr, i + 1, high)
    __UNDEF__('partition', __FRAME__(), 33)
    return i

def main():
    __DEF__('main', line_no=36, frame=__FRAME__())
    __ARG__('main', __FRAME__(), 36)
    unsorted = [3, 6, 8, 10, 1, 2, 5]
    __AS__('unsorted = [3, 6, 8, 10, 1, 2, 5]', 'unsorted', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=37)
    __PRINT__(38, __FRAME__(), f'Unsorted: {unsorted}')
    q_sorted = __FC__('quicksort(unsorted.copy())', quicksort, locals(), globals(), __FRAME__(), 39, unsorted.copy())
    __AS__('q_sorted = __FC__(@quicksort(unsorted.copy())@, quicksort, locals(), globals(), __FRAME__(), 39, unsorted.copy())', 'q_sorted', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=39)
    __PRINT__(40, __FRAME__(), f'Sorted: {q_sorted}')
    __UNDEF__('main', __FRAME__(), 40)
    return None
if __name__ == '__main__':
    __FC__('main()', main, locals(), globals(), __FRAME__(), 44)