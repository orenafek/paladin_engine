# @Paladin.postcond('n', 'n > 0')
# def square(n):
#     return n * n


def power(n, p):
    """

    :param n:
    :param p:
    :return:
    """
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
        n *= n
    return n


print(power(2, 5))
