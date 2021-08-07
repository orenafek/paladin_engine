from stubs.stubs import __FLI__, __POST_CONDITION__, __FC__, __AS__, __FRAME__


class Point(object):

    def __init__(self):
        self._x = 0
        __AS__('self._x = 0', 'self._x', locals=locals(), globals=globals(), frame=__FRAME__, line_no=9)
        self._y = 0
        __AS__('self._y = 0', 'self._y', locals=locals(), globals=globals(), frame=__FRAME__, line_no=9)

    def setX(self, x):
        self._x = x
        __AS__('self._x = x', 'self._x', locals=locals(), globals=globals(), frame=__FRAME__, line_no=13)

    def setY(self, y):
        self._y = y
        __AS__('self._y = y', 'self._y', locals=locals(), globals=globals(), frame=__FRAME__, line_no=16)

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def __str__(self):
        return '({x},{y})'.format(x=self._x, y=self._y)

def main():
    p0 = __FC__('Point()', Point, locals(), globals(), __FRAME__, 29)
    __AS__('p0 = Point()', 'p0', locals=locals(), globals=globals(), frame=__FRAME__, line_no=29)
    __FC__('p0.setX(1)', p0.setX, locals(), globals(), __FRAME__, 30, 1)
    __FC__('p0.setY(2)', p0.setY, locals(), globals(), __FRAME__, 31, 2)
    p0._y = 4
    __AS__('p0._y = 4', 'p0._y', locals=locals(), globals=globals(), frame=__FRAME__, line_no=29)
    __FC__('print(p0)', print, locals(), globals(), __FRAME__, 34, p0)
if __name__ == '__main__':
    __FC__('main()', main, locals(), globals(), __FRAME__, 38)