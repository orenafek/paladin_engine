from typing import Set


def pour_even(l: Set[int]):
    l1 = set()
    b = True
    while l:
        x = l.pop()
        if x % 2 == 0:
            l1.add(x)

    if b:
        l1.add(12)
        b = False

    return l1


def main():
    l = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    print(pour_even(l))


if __name__ == '__main__':
    main()
