class A:
    def __init__(self, x: int):
        self.x = x


class B:
    def __init__(self, a):
        self.a = a


class C:
    def __init__(self, b):
        self.b = b


def main():
    a = A(1)
    b = B(a)
    c = C(b)

    for i in range(100):
        a.x = 2 * i
        print(c.b.a.x)
        b.a.x = 3 * i
        print(c.b.a.x)
        c.b.a.x = 4 * i
        print(c.b.a.x)


if __name__ == '__main__':
    main()
