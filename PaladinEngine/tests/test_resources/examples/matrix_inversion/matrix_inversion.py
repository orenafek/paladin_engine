def id_mat(n):
    """Returns a matrix with ones on the main diagonal and zeros elsewhere."""
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def mat_mult(A, B):
    """Performs matrix multiplication."""
    res = []
    for i in range(len(A)):
        r = []
        for j in range(len(B[0])):
            s = 0
            for k in range(len(B)):
                s += A[i][k] * B[k][j]
            r.append(s)
        res.append(r)
    return res


def invert(mat):
    n = len(mat)
    aug_mat = [r + id_mat(n)[i] for i, r in enumerate(mat)]

    for c in range(n):
        pivot_row = max(range(c, n), key=lambda i: abs(aug_mat[i][c]))
        tmp = aug_mat[pivot_row]
        aug_mat[pivot_row] = aug_mat[c]
        aug_mat[c] = tmp

        pivot_val = aug_mat[c][c]
        aug_mat[c] = [e / pivot_val for e in aug_mat[c]]

        for r in range(n):
            if r != c:
                f = aug_mat[r][c]
                aug_mat[r] = [aug_mat[r][i] - f * aug_mat[c][i] for i in range(n)]  # Bug: Incorrect range

    inv_mat = []
    for r in aug_mat:
        inv_mat.append([round(e, 2) for e in r[n:]])  # Adjusted: Rounding each element to 2 decimal places
    return inv_mat


def main():
    # Example usage
    m = [
        [1, 2, 3],
        [0, 1, 4],
        [5, 6, 0]
    ]

    inv_m = invert(m)
    for r in inv_m:
        print(r)

    if mat_mult(m, inv_m) != id_mat(3):
        raise RuntimeError('Wrong inv_m :(')


if __name__ == '__main__':
    main()
