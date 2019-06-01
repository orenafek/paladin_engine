def __AS__(*a):
    ...


def __FLI__(*a, **b):
    ...

def power(n, p):
    """

    :param n:
    :param p:
    :return:
    """
    result = 1
    __AS__(('result', result))
    for i in range(p):
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
        __AS__(('result', result))
        if i == 2:
            result = -1
            __AS__(('result', result))
    return result


print(power(2, 5))