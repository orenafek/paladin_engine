# @Paladin.postcond('n', 'n > 0')
# def square(n):
#     return n * n


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
            loop-invariant(n):
                if |n| >= 1:
                    n >= pre(n)
                else:
                    n < pre(n)
        @@@
        """
        result = result * n
        x, y = result, result / 2
        z, [x, y] = 4, [1, 2]
    return result


print(power(2, 5))
