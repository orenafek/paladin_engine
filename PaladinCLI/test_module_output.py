from stubs.stubs import __FLI__, __POST_CONDITION__, __FC__, __AS__, __FRAME__


def power(n, p):
    """

    :param n:
    :param p:
    :return:
    """
    result = 1
    __AS__('result = 1', 'result', locals=locals(), globals=globals(), frame=__FRAME__, line_no=8)
    __iter = __FC__('range(p)', range, locals(), globals(), __FRAME__, 9, p).__iter__()
    while True:
        try:
            i = __iter.__next__()
        except StopIteration:
            break
        __FLI__(locals=locals(), globals=globals())
        ' \n        @@@\n           loop-invariant:\n               if |n| >= 1:\n                   result >= pre(result)\n               else:\n                   result < pre(result)\n        @@@\n        '
        result = result * n
        __AS__('result = result * n', 'result', locals=locals(), globals=globals(), frame=__FRAME__, line_no=10)
        if i == 2:
            result = -1
            __AS__('result = -1', 'result', locals=locals(), globals=globals(), frame=__FRAME__, line_no=21)
    return result
__FC__('print(power(2, 5))', print, locals(), globals(), __FRAME__, 26, power(2, 5))