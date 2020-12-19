# @Paladin.postcond('n', 'n > 0')
# def square(n):
#     return n * n
import abc

from PaladinEngine.api.api import Paladinize
from pycallgraph import PyCallGraph, GlobbingFilter, Config
from pycallgraph.output import  GraphvizOutput


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