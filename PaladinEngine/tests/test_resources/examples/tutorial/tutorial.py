from random import randint, seed
from typing import Set


class Array(object):
    def __init__(self, size: int):
        self.data = [0 for _ in range(size)]
        self.dim = size
        self._populate()

    def sort(self):
        for i in range(self.dim):
            for j in range(0, self.dim - i - 1):
                if self.data[j] > self.data[j + 1]:
                    self.data[j], self.data[j + 1] = self.data[j + 1], self.data[j]

        x = 0
        while True:
            x += 1
            print(x)
            if x > 10:
                break

    def _populate(self):
        for i in range(self.dim):
            self.data[i] = randint(0, 100)

    def __repr__(self):
        return repr(self.data)


def sort_array():
    seed(2024)
    a = Array(8)
    print(a)
    a.sort()
    print(a)


def pour_even(s: Set[int]):
    s1 = set()
    b = True
    while s:
        x = s.pop()
        if x % 2 == 0:
            s1.add(x)

    if b:
        s1.add(12)
        b = False

    return s1


def pour_even_example():
    nums = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    print(pour_even(nums))


def main():
    sort_array()
    pour_even_example()


if __name__ == '__main__':
    main()
