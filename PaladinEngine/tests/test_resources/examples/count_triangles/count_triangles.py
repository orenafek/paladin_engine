def solution(A):
    if len(A) < 3:
        return 0

    a_sorted = sorted(A)
    sort_map = {}
    for i in range(len(a_sorted)):
        sort_map[i] = A.index(a_sorted[i])

    sums = {}
    for i in range(len(a_sorted) - 2):
        sums[i] = []
        r = range(i + 1, len(A) - 1)
        for j in r:
            sums[i] = sums[i] + [(j, a_sorted[i] + a_sorted[j])]
    print(f'sums = {sums}')

    for i in sums:
        for s in sums[i]:
            if s[1] > a_sorted[s[0] + 1]:
                print(sorted([sort_map[i], sort_map[s[0]], sort_map[s[0] + 1]]))


if __name__ == '__main__':
    solution([10, 2, 5, 1, 8, 20])
    solution([20, 1, 10, 2, 5, 8])
