from stubs.stubs import __AC__, __ARG__, __AS__, __BMFCS__, __BREAK__, __DEF__, __EOLI__, __FC__, __FLI__, __FRAME__, __IS_STUBBED__, __PAUSE__, __PIS__, __PRINT__, __RESUME__, __SOL__, __SOLI__, __UNDEF__


class Point(object):

    def __init__(self, x, y):
        __DEF__('__init__', line_no=2, frame=__FRAME__())
        __PIS__(self, 'self', line_no=2)
        __ARG__('__init__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=2)
        __ARG__('__init__', 'x', x, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=2)
        __ARG__('__init__', 'y', y, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=2)
        self.x = x
        __AS__('self.x = x', 'self.x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=3)
        self.y = y
        __AS__('self.y = y', 'self.y', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=4)
        __UNDEF__('__init__', __FRAME__(), 4)
        return None

    def __add__(self, other):
        __DEF__('__add__', line_no=6, frame=__FRAME__())
        __ARG__('__add__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=6)
        __ARG__('__add__', 'other', other, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=6)
        if __FC__('isinstance(other, Point)', isinstance, locals(), globals(), __FRAME__(), 7, other, Point):
            __UNDEF__('__add__', __FRAME__(), 8)
            return __FC__('Point(self.x + other.x, self.y + other.y)', Point, locals(), globals(), __FRAME__(), 8, self.x + other.x, self.y + other.y)
        __UNDEF__('__add__', __FRAME__(), 8)
        return None

    def __neg__(self):
        __DEF__('__neg__', line_no=10, frame=__FRAME__())
        __ARG__('__neg__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=10)
        __UNDEF__('__neg__', __FRAME__(), 11)
        return __FC__('Point(-1 * self.x, -1 * self.y)', Point, locals(), globals(), __FRAME__(), 11, -1 * self.x, -1 * self.y)

    def __sub__(self, other):
        __DEF__('__sub__', line_no=13, frame=__FRAME__())
        __ARG__('__sub__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=13)
        __ARG__('__sub__', 'other', other, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=13)
        if __FC__('isinstance(other, Point)', isinstance, locals(), globals(), __FRAME__(), 14, other, Point):
            __UNDEF__('__sub__', __FRAME__(), 15)
            return self + -other
        __UNDEF__('__sub__', __FRAME__(), 15)
        return None

    def __repr__(self):
        __DEF__('__repr__', line_no=17, frame=__FRAME__())
        __ARG__('__repr__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=17)
        __UNDEF__('__repr__', __FRAME__(), 18)
        return f'{self.x}, {self.y}'
if __name__ == '__main__':
    point = __FC__('Point(1, 2)', Point, locals(), globals(), __FRAME__(), 21, 1, 2)
    __AS__('point = __FC__(@Point(1, 2)@, Point, locals(), globals(), __FRAME__(), 21, 1, 2)', 'point', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=21)
    point.x = 0
    __AS__('point.x', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=22)
    __PRINT__(23, __FRAME__(), point)