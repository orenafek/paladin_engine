from typing import Any


class A(object):
    def __init__(self, s: str):
        self.s = s


def secondary():
    z = 5
    z = 6


def main():
    x = 1
    y = 2
    secondary()
    x = 3
    y = 4

    print(f'(x, y) = {x, y}')

    a = A('a')

    a.s = 'b'

    x = 7
    y = 8

    a.s = 'c'

    print(f'a.s = {a.s}')


if __name__ == '__main__':
    main()
