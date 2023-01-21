
def caterp(a):  # better solution O(n)
    n = len(a)
    i, j = 0, 0
    k = 1
    total_slices = 0
    seen = set()
    while j < n:
        seen = seen | {a[j]}
        if j == n - 1:
            total_slices += plus1over2(k)
        elif a[j + 1] in seen:  # a[j+1] is already in range i..j
            i0 = i
            while a[j + 1] in seen:
                seen = seen - {a[i]}
                i += 1
                k -= 1
            total_slices += plus1over2(j + 1 - i0) - plus1over2(j + 1 - i)
        k += 1
        j += 1

    return total_slices


def plus1over2(k):
    return k * (k + 1) / 2


if __name__ == '__main__':
    sample = [3, 4, 3, 5, 4]
    caterp_result = caterp(sample)
