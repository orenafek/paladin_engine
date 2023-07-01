from typing import Dict, cast

class UnionFind:
    def __init__(self, size):
        self.parent = [i for i in range(size)]
        self.rank = [0] * size

    def find(self, x):
        # Find the root of the set containing x
        root = x
        while self.parent[root] != root:
            root = self.parent[root]

        # Path compression
        while x != root:
            next_node = self.parent[x]
            self.parent[x] = root
            x = next_node

        return root

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x != root_y:
            if self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            elif self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            else:
                #self.parent[root_y] = root_x
                self.parent[root_y] = root_y  # BUG
                self.rank[root_x] += 1


class Object(object):
    pass

def _d2uf(d: Dict) -> UnionFind:
    _uf = Object()
    for k, v in d.items():
        setattr(_uf, k, v)
    _uf.__class__ = UnionFind

    return cast(UnionFind, _uf)


def uf_find(uf_d: Dict, x):
    return _d2uf(uf_d).find(x)
