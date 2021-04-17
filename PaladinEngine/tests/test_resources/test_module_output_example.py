from stubs import __AS__, __FCS__, __FLI__, __POST_CONDITION__
import sys


def power(n, p):
    """

    :param n:
    :param p:
    :return:
    """
    result = 1
    __AS__('result', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=8)
    ____0 = range(p)
    __FCS__(name='range', args=[p], kwargs=[], return_value=____0, frame=sys._getframe(0), locals=locals(),
            globals=globals(), line_no=9)
    __iter = ____0.__iter__()
    while True:
        try:
            i = __iter.__next__()
        except StopIteration:
            break
    __FLI__(locals=locals(), globals=globals())
    '\n        @@@\n           loop-invariant:\n               if |n| >= 1:\n                   result >= pre(' \
    'result)\n               else:\n                   result < pre(result)\n        @@@\n '
    result = result * n
    __AS__('result', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=10)
    if i == 2:
        result = -1
        __AS__('result', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=21)
    return result


____1 = power(2, 5)
__FCS__(name='power', args=[2, 5], kwargs=[], return_value=____1, frame=sys._getframe(0), locals=locals(),
        globals=globals(), line_no=26)
print(____1)