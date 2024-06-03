from stubs.stubs import __AC__, __ARG__, __AS__, __BMFCS__, __BREAK__, __DEF__, __EOLI__, __FC__, __FLI__, __FRAME__, __IS_STUBBED__, __PAUSE__, __PIS__, __PRINT__, __RESUME__, __SOL__, __SOLI__, __UNDEF__


from random import randint, seed
from typing import Set

class Array(object):

    def __init__(self, size: int):
        __DEF__('Array.__init__', line_no=6, frame=__FRAME__())
        __ARG__('Array.__init__', __FRAME__(), 6, self=self, size=size)
        self.data = [0 for _ in __FC__('range(size)', range, locals(), globals(), __FRAME__(), 7, size)]
        __AS__('self.data = [0 for _ in __FC__(@range(size)@, range, locals(), globals(), __FRAME__(), 7, size)]', 'self.data', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=7)
        self.dim = size
        __AS__('self.dim = size', 'self.dim', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=8)
        self.sum = 0
        __AS__('self.sum = 0', 'self.sum', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=9)
        self.min = 0
        __AS__('self.min = 0', 'self.min', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=10)
        self.max = 0
        __AS__('self.max = 0', 'self.max', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=11)
        __FC__('self.populate()', self.populate, locals(), globals(), __FRAME__(), 12)
        __UNDEF__('Array.__init__', __FRAME__(), 12)
        return None

    def sort(self):
        __DEF__('Array.sort', line_no=14, frame=__FRAME__())
        __ARG__('Array.sort', __FRAME__(), 14, self=self)
        __SOL__(__FRAME__(), 15)
        for __iter_3 in __FC__('range(self.dim)', range, locals(), globals(), __FRAME__(), 15, self.dim):
            __SOLI__(15, __FRAME__())
            i = __iter_3
            __AS__('i = __iter_3', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=15)
            __SOL__(__FRAME__(), 16)
            for __iter_2 in __FC__('range(0, self.dim - i - 2)', range, locals(), globals(), __FRAME__(), 16, 0, self.dim - i - 2):
                __SOLI__(16, __FRAME__())
                j = __iter_2
                __AS__('j = __iter_2', 'j', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=16)
                if self.data[j] > self.data[j + 1]:
                    (self.data[j], self.data[j + 1]) = (self.data[j + 1], self.data[j])
                    __AS__('(self.data[j], self.data[j + 1]) = (self.data[j + 1], self.data[j])', 'self.data[j + 1]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=18)
                    __AS__('(self.data[j], self.data[j + 1]) = (self.data[j + 1], self.data[j])', 'self.data[j]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=18)
                __EOLI__(__FRAME__(), loop_start_line_no=16, loop_end_line_no=18)
            __EOLI__(__FRAME__(), loop_start_line_no=15, loop_end_line_no=18)
        __UNDEF__('Array.sort', __FRAME__(), 18)
        return None

    def populate(self):
        __DEF__('Array.populate', line_no=20, frame=__FRAME__())
        __ARG__('Array.populate', __FRAME__(), 20, self=self)
        __FC__('seed(2024)', seed, locals(), globals(), __FRAME__(), 21, 2024)
        __SOL__(__FRAME__(), 22)
        for __iter_1 in __FC__('range(self.dim)', range, locals(), globals(), __FRAME__(), 22, self.dim):
            __SOLI__(22, __FRAME__())
            i = __iter_1
            __AS__('i = __iter_1', 'i', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=22)
            self.data[i] = __FC__('randint(0, 100)', randint, locals(), globals(), __FRAME__(), 23, 0, 100)
            __AS__('self.data[i] = __FC__(@randint(0, 100)@, randint, locals(), globals(), __FRAME__(), 23, 0, 100)', 'self.data[i]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=23)
            __EOLI__(__FRAME__(), loop_start_line_no=22, loop_end_line_no=23)
        self.sum = __FC__('sum(self.data)', sum, locals(), globals(), __FRAME__(), 24, self.data)
        __AS__('self.sum = __FC__(@sum(self.data)@, sum, locals(), globals(), __FRAME__(), 24, self.data)', 'self.sum', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=24)
        self.min = __FC__('min(self.data)', min, locals(), globals(), __FRAME__(), 25, self.data)
        __AS__('self.min = __FC__(@min(self.data)@, min, locals(), globals(), __FRAME__(), 25, self.data)', 'self.min', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=25)
        self.max = __FC__('max(self.data)', max, locals(), globals(), __FRAME__(), 26, self.data)
        __AS__('self.max = __FC__(@max(self.data)@, max, locals(), globals(), __FRAME__(), 26, self.data)', 'self.max', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=26)
        __UNDEF__('Array.populate', __FRAME__(), 26)
        return None

    def __repr__(self):
        __DEF__('Array.__repr__', line_no=28, frame=__FRAME__())
        __ARG__('Array.__repr__', __FRAME__(), 28, self=self)
        __UNDEF__('Array.__repr__', __FRAME__(), 29)
        return __FC__('repr(self.data)', repr, locals(), globals(), __FRAME__(), 29, self.data)

def sort_array():
    __DEF__('sort_array', line_no=32, frame=__FRAME__())
    __ARG__('sort_array', __FRAME__(), 32)
    a = __FC__('Array(14)', Array, locals(), globals(), __FRAME__(), 33, 14)
    __AS__('a = __FC__(@Array(14)@, Array, locals(), globals(), __FRAME__(), 33, 14)', 'a', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=33)
    __FC__('a.sort()', a.sort, locals(), globals(), __FRAME__(), 34)
    if __FC__('sorted(a.data)', sorted, locals(), globals(), __FRAME__(), 35, a.data) == a.data:
        __PRINT__(36, __FRAME__(), 'a is sorted :)')
    else:
        __PRINT__(38, __FRAME__(), 'a is not sorted :(')
    __UNDEF__('sort_array', __FRAME__(), 38)
    return None

def pour_even(s: Set[int]):
    __DEF__('pour_even', line_no=41, frame=__FRAME__())
    __ARG__('pour_even', __FRAME__(), 41, s=s)
    s1 = set()
    __AS__('s1 = set()', 's1', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=42)
    __SOL__(__FRAME__(), 43)
    while s:
        __SOLI__(43, __FRAME__())
        x = __BMFCS__(__FC__('s.pop()', s.pop, locals(), globals(), __FRAME__(), 44), s, 's', 'pop', 44, __FRAME__(), locals(), globals())
        __AS__('x = __BMFCS__(__FC__(@s.pop()@, s.pop, locals(), globals(), __FRAME__(), 44), s, @s@, @pop@, 44, __FRAME__(), locals(), globals())', 'x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=44)
        if x % 2 == 0:
            __BMFCS__(__FC__('s1.add(x)', s1.add, locals(), globals(), __FRAME__(), 46, x), s1, 's1', 'add', 46, __FRAME__(), locals(), globals(), x)
        if __FC__('len(s)', len, locals(), globals(), __FRAME__(), 48, s) == 0:
            __BMFCS__(__FC__('s1.add(12)', s1.add, locals(), globals(), __FRAME__(), 49, 12), s1, 's1', 'add', 49, __FRAME__(), locals(), globals(), 12)
        __EOLI__(__FRAME__(), loop_start_line_no=43, loop_end_line_no=49)
    __UNDEF__('pour_even', __FRAME__(), 51)
    return s1

def pour_even_example():
    __DEF__('pour_even_example', line_no=54, frame=__FRAME__())
    __ARG__('pour_even_example', __FRAME__(), 54)
    nums = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    __AS__('nums = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}', 'nums', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=55)
    __PRINT__(56, __FRAME__(), 'nums: ', nums)
    __PRINT__(57, __FRAME__(), 'Even nums:', pour_even(nums))
    __UNDEF__('pour_even_example', __FRAME__(), 57)
    return None

def main():
    __DEF__('main', line_no=60, frame=__FRAME__())
    __ARG__('main', __FRAME__(), 60)
    __FC__('seed(2024)', seed, locals(), globals(), __FRAME__(), 61, 2024)
    __FC__('sort_array()', sort_array, locals(), globals(), __FRAME__(), 62)
    __PRINT__(63, __FRAME__(), '--------')
    __FC__('pour_even_example()', pour_even_example, locals(), globals(), __FRAME__(), 64)
    __UNDEF__('main', __FRAME__(), 64)
    return None
if __name__ == '__main__':
    __FC__('main()', main, locals(), globals(), __FRAME__(), 68)