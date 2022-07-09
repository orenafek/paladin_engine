from copy import deepcopy
from typing import *


class Matrix2D(object):

    def __init__(self, m: int, n: int, empty_value: object = 0):
        self.m = m
        self.n = n
        self._empty_value = empty_value
        self._data = [empty_value for _ in range(m * n)]

    def _inner_index(self, key):
        return key[0] * self.n + key[1]

    def __setitem__(self, key, value):
        temp = deepcopy(self._data)
        temp[self._inner_index(key)] = value
        self._data = temp

    def __getitem__(self, item) -> object:
        return self._data[self._inner_index(item)]

    def _cell_op(self, other: 'Matrix2D', op: Callable):
        if not self._same_dim(other):
            raise Matrix2D.DimensionError()

        result = Matrix2D(self.m, self.n)

        for i, j in zip(range(result.m), range(result.n)):
            result[i, j] = op(self[i, j], other[i, j])

        return result

    def __add__(self, other):
        return self._cell_op(other, op=lambda x, y: x + y)

    def __sub__(self, other):
        return self._cell_op(other, op=lambda x, y: x - y)

    def __mul__(self, other: Union['Matrix2D', object]) -> 'Matrix2D':
        if not isinstance(other, Matrix2D) or other.n != self.n:
            raise Matrix2D.DimensionError()

        result = Matrix2D(self.m, other.n, empty_value=self._empty_value)

        for i, j in zip(range(result.m), range(result.n)):
            result[i, j] = sum([self[i, k] * other[k, j] for k in range(self.n)])

        return result

    def __str__(self):
        return '[' + '\n\t '.join([', '.join([str(self[i, j]) for j in range(self.n)]) for i in range(self.m)]) + ']'

    def submat(self, i: int, j: int):
        result = Matrix2D(self.m - 1, self.n - 1)

        for s, t in zip(range(result.m), range(result.n)):
            if s == i or t == j:
                continue
            result[s, t] = self[s, t]

        return result

    def det(self):
        if self.m != self.n:
            raise Matrix2D.DimensionError('det is only for m == n')

        def det_inner(mat: Matrix2D):
            if mat.m == 1:
                result = mat[0, 0]

            elif mat.m == 2:
                result = mat[0, 0] * mat[1, 1] - mat[0, 1] * mat[1, 0]

            else:
                result = sum([(-1)**j * mat[0, j] * det_inner(self.submat(0, j)) for j in range(self.n)])

            return result

        return det_inner(self)

    class DimensionError(ValueError):
        pass

    def _same_dim(self, other: 'Matrix2D'):
        return self.m == other.m and self.n == other.n

def main():
    A = Matrix2D(1, 2)
    A[0, 0] = 1
    A[0, 1] = 2

    print('A = ' + str(A))

    B = Matrix2D(2, 2)
    B[0, 0] = 3
    B[0, 1] = 4
    B[1, 0] = 5
    B[1, 1] = 6

    print('B = ' + str(B))

    print('A * B = ' + str(A * B))

    print('det(B) = ' + str(B.det()))

    C = Matrix2D(3, 3)
    for i in range(C.m):
        for j in range(C.n):
            C[i, j] = C.m * i + j

    print('C = ' + str(C))
    print('det(C) = ' + str(C.det()))

if __name__ == '__main__':
    main()