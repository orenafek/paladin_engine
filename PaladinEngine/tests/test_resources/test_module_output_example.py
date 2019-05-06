def power(n, p):
    """

    :param n:
    :param p:
    :return:
    """
    result = 1
    __AS__(('result', result))
    for i in range(p):
        __FLI__(i)
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
        __AS__(('result', result))
    return result


print(power(2, 5))
