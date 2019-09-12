# @Paladin.postcond('n', 'n > 0')
# def square(n):
#     return n * n
from PaladinEngine.api.api import Paladinize


@Paladinize
class X(object):
    pass

def power(n, p):
    """

    :param n:
    :param p:
    :return:
    """
    result = 1
    for i in range(p):
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
        if i == 2:
            result = -1

    return result


print(power(2, 5))
