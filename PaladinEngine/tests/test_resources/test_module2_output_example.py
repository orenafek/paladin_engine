def __AS__(*args, **kwargs):
    pass


import sys


def power(n, p):
    """

    :param n:
    :param p:
    :return:
    """
    result = 1
    __AS__(('result', result), locals=locals(), globals=globals(), frame=
    sys._getframe(0), line_no=9)
    __iter = range(p).__iter__()
    __AS__(('__iter', __iter), locals=locals(), globals=globals(), frame=
    sys._getframe(0), line_no=9)
    while True:
        try:
            i = __iter.__next__()
            __AS__(('i', i), locals=locals(), globals=globals(), frame=sys.
                   _getframe(0), line_no=4)
        except StopIteration:
            break
        __FLI__(locals=locals(), globals=globals())
        """ 
            @@@
               loop-invariant:
                   if |n| >= 1:
                       result >= pre(result)
                   else:
                       result < pre(result)
            @@@
            """
        result = result * n
        __AS__(('result', result), locals=locals(), globals=globals(),
               frame=sys._getframe(0), line_no=20)
        if i == 2:
            result = -1
            __AS__(('result', result), locals=locals(), globals=globals(),
                   frame=sys._getframe(0), line_no=23)
    return result


print(power(2, 5))
