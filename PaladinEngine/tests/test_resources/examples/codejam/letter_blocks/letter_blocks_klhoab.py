from collections import *
from functools import *
from itertools import *
import math

INDEX = -1

def input():
    global INDEX

    inp = """6
    5
    CODE JAM MIC EEL ZZZZZ
    6
    CODE JAM MIC EEL ZZZZZ EEK
    2
    OY YO
    2
    HASH CODE
    6
    A AA BB A BA BB
    2
    CAT TAX
    """
    INDEX += 1
    return inp.split('\n')[INDEX]


def solve():
    n = int(input())
    arr = input().split()

    def check(t):
        d = defaultdict(list)
        for i, c in enumerate(t):
            d[c] += [i]
        flag = 0
        for _, arr in d.items():
            for j in range(len(arr) - 1):
                if arr[j] != arr[j + 1] - 1:
                    flag = 1
        return not flag

    while len(list(arr)) > 1:
        t = ""
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # print(n,i,j, arr)
                if arr[i][-1] == arr[j][0]:
                    t = arr[i] + arr[j]
                    if not check(t):
                        return "IMPOSSIBLE"
                    arr.pop(max(i, j))
                    arr.pop(min(i, j))
                    arr += [t]
                    n -= 1
                    break
            if t:
                break

        if t == "":
            t = arr[0] + arr[1]
            if not check(t):
                return "IMPOSSIBLE"
            arr.pop(1)
            arr.pop(0)
            arr += [t]
            n -= 1

    return arr[0]


if __name__ == "__main__":
    N = int(input())
    for g in range(N):
        print(f"Case #{g + 1}: {solve()}")
