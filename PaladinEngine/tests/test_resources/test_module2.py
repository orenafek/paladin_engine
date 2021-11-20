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


def main():
    p0 = Point()
    p0.setX(1)
    p0.setY(2)
    #p0._y = 4

    r0 = Rectangle(1,2,3,4)
    #r0.rt.setX(5)
    print(r0.rt.getX())
    print(r0.rt._x)

    x = y = z = 3
    # TODO: Post order.
    # __FC__(__FA__(r0, 'rt',...), 'setX', 5, ...)

    print(p0)


if __name__ == '__main__':
    archive.resume_record()
    main()
