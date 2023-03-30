def f():
    for i in range(5):
        print(i)


def g():
    for i in range(5, 11):
        print(i)


def square(x: float):
    return x * x


def h():
    for x in range(1, 11):
        y = square(x)
        print(y)


if __name__ == '__main__':
    f()
    g()
    h()
