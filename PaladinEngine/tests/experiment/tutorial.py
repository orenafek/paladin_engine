from random import randint, seed
from typing import Set


class Array(object):
    def __init__(self, size: int):
        self.data = [0 for _ in range(size)]
        self.dim = size
        self.sum = 0
        self.min = 0
        self.max = 0
        self.populate()

    def sort(self):
        for i in range(0, self.dim):
            for j in range(0, self.dim - i - 2):
                if self.data[j] > self.data[j + 1]:
                    self.data[j], self.data[j + 1] = self.data[j + 1], self.data[j]

    def populate(self):
        seed(2024)
        for i in range(self.dim):
            self.data[i] = randint(0, 100)
        self.min = min(self.data)
        self.max = max(self.data)
        self.sum = sum(self.data)

    def __repr__(self):
        return repr(self.data)


def sort_array():
    a = Array(14)
    a.sort()
    if sorted(a.data) == a.data:
        print('a is sorted :)')
    else:
        print('a is not sorted :(')


def pour_even(s: Set[int]):
    s1 = set()
    while s:
        x = s.pop()
        if x % 2 == 0:
            s1.add(x + 2)

        if len(s) == 0:
            s1.add(12)

    return s1


def pour_even_example():
    nums = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    print('nums: ', nums)
    print('Even nums:', pour_even(nums))


def main():
    seed(2024)
    sort_array()
    print('--------')
    pour_even_example()


if __name__ == '__main__':
    main()
