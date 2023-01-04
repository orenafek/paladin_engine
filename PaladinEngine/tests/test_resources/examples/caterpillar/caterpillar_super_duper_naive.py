
def super_duper_naive(a):
    total_slices = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            if len(set(a[i:j])) == j - i:
                total_slices += 1

    return total_slices


if __name__ == '__main__':
    sample = [3, 4, 3, 5, 4]
    sdn = super_duper_naive(sample)
