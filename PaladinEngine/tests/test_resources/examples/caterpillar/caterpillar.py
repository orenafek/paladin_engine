def super_duper_naive(a):
    total_slices = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            if len(set(a[i:j])) == j - i:
                total_slices += 1

    return total_slices


def super_naive(a):
    total_slices = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            if len(set(a[i:j])) == j - i:
                total_slices += 1
            else:
                break

    return total_slices


def naive(a):  # straightforward solution O(n^2)
    n = len(a)
    i, j = 0, 0
    total_slices = 0
    seen = set()
    while j < n:
        seen = seen | set([a[j]])
        total_slices += 1
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


# @pytest.mark.randomize(a=list_of(int, items=1000), ncalls=10)
# def test(a: typing.List[int]):
#     print(f'a = {a}')
#     n = naive(a)
#     print(f'naive = {n}')
#     c = caterp(a)
#     print(f'caterp = {c}')
#     assert n == c

def main():
    sample = [3, 4, 3, 5, 4]
    sdn = super_duper_naive(sample)
    sn = super_naive(sample)
    n = naive(sample)
    c = caterp(sample)
    print(f'sdn = {sdn} sn = {sn} n = {n}, c = {c}')
    assert sdn == sn == n == c

if __name__ == '__main__':
    main()

