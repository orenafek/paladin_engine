def naive(a):  # straightforward solution O(n^2)
    n = len(a)
    i, j = 0, 0
    total_slices = 0
    seen = set()
    while j < n:
        seen = seen | set([a[j]])
        total_slices += 1
        print(i, j)
        if j == n - 1 or a[j + 1] in seen:
            i += 1
            j = i
            seen = set()
        else:
            j += 1

    return total_slices


def caterp(a):  # better solution O(n)
    n = len(a)
    i, j = 0, 0
    k = 1
    total_slices = 0
    seen = set()
    while j < n:
        seen = seen | set([a[j]])
        print(i, j)
        if j == n - 1:
            print('end', k)
            total_slices += k * (k + 1) / 2
        elif a[j + 1] in seen:  # a[j+1] is already in range i..j
            print('middle', k)

            # total_slices += plus1over2(k)  # k * (k + 1) / 2
            print('kij', k, i, j)
            i0 = i
            while a[j + 1] in seen:
                seen = seen - set([a[i]])
                i += 1
                k -= 1

            print('kij', k, i, j)

            # total_slices -= plus1over2(k)   # k * (k + 1) / 2
            total_slices += plus1over2(j + 1 - i0) - plus1over2(j + 1 - i)
            # total_slices += (2 * (j + 1) - (i + i0) - 1) * (i - i0) / 2

            print('---', k)
        k += 1
        j += 1

    return total_slices


def plus1over2(k):
    return k * (k + 1) / 2


if __name__ == '__main__':
    sample = [3, 4, 2, 5, 4]
    naive(sample)
    caterp(sample)
