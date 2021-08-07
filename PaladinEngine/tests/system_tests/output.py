class Point(object):

    def __init__(self):
        self._x = 0
        __SIMPLE_AS__('self._x', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=9)
        self._y = 0
        __SIMPLE_AS__('self._y', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=9)

    def setX(self, x):
        self._x = x
        __SIMPLE_AS__('self._x', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=13)

    def setY(self, y):
        self._y = y
        __SIMPLE_AS__('self._y', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=16)

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def __str__(self):
        return '({x},{y})'.format(x=self._x, y=self._y)

def main():
    ____0 = Point()
    __FCS__(name='Point', args=[], kwargs=[], return_value=____0, frame=sys._getframe(0), locals=locals(), globals=globals(), line_no=29)
    p0 = ____0
    __SIMPLE_AS__('p0', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=29)
    p0.setX(1)
    p0.setY(2)
    p0._y = 4
    __SIMPLE_AS__('p0._y', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=29)
    print(p0)
if __name__ == '__main__':
    main()