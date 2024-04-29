from random import randint


class Array(object):
    def __init__(self, size: int):
        self.data = [0 for _ in range(size)]
        self.dim = size
        self._populate()

    def sort(self):
        for i in range(self.dim):
            for j in range(0, self.dim - i - 1):
                x = 3
                if self.data[j] > self.data[j + 1]:
                    self.data[j], self.data[j + 1] = self.data[j + 1], self.data[j]

    def _populate(self):
        for i in range(self.dim):
            self.data[i] = randint(0, 100)

    def __repr__(self):
        return repr(self.data)


def main():
    a = Array(8)
    print(a)
    a.sort()
    print(a)


if __name__ == '__main__':
    main()
