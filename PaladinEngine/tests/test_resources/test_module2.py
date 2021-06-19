# @Paladin.postcond('n', 'n > 0')
# def square(n):
#     return n * n


# @Paladin
class Point(object):
    def __init__(self):
        self._x = 0
        self._y = 0

    def setX(self, x):
        self._x = x

    def setY(self, y):
        self._y = y

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def __str__(self):
        return '({x},{y})'.format(x=self._x, y=self._y)


def main():
    p0 = Point()
    p0.setX(1)
    p0.setY(2)
    p0._y = 4

    print(p0)


if __name__ == '__main__':
    main()
