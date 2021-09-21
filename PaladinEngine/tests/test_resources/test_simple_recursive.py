def f():
    g()
    i()


def g(b: bool = True):
    h()
    if b:
        for i in range(4):
            k()


def h():
    t()


def t():
    pass


def i():
    pass


def k():
    g(False)


if __name__ == '__main__':
    f()
