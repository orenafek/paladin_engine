
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


if __name__ == '__main__':
    sample = [3, 4, 3, 5, 4]
    c_naive = naive(sample)
