# @Paladin.postcond('n', 'n > 0')
# def square(n):
#     return n * n
from stubs.stubs import archive

archive.pause_record()


# @Paladin
class Point(object):
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

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


class Rectangle(object):
    def __init__(self, left, bottom, right, top):
        self.lb = Point(left, bottom)
        self.rt = Point(right, top)

    def __repr__(self):
        return f'(lb: {self.lb}, rt: {self.rt})'

def main():
    p0 = Point()
    p0.setX(1)
    p0.setY(2)

    r0 = Rectangle(1, 2, 3, 4)
    print(r0)
    r0.rt = Point(-1, -2)
    print(r0)
    for i in range(4):
        r0.rt = Point(i, i + 1)
        print(r0)

    r0.rt.setX(4)

    r0.rt = p0
    r0.rt.setX(9)

    print(r0)


if __name__ == '__main__':
    archive.resume_record()
    main()
