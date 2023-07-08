from copy import copy
from functools import reduce
from typing import Dict, cast, List, Type, Any


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
                # self.parent[root_y] = root_x
                self.parent[root_y] = root_y  # BUG
                self.rank[root_x] += 1


class Edge:
    def __init__(self, src, dest, weight):
        self.src = src
        self.dest = dest
        self.weight = weight

    def __repr__(self):
        return f'{self.src}-[{self.weight}]-{self.dest}'


class Object(object):
    pass


def _d2obj(d: Dict, t: Type) -> Any:
    _obj = Object()
    for k, v in d.items():
        setattr(_obj, k, v)
    _obj.__class__ = t

    return cast(t, _obj)


def has_cycle(g_d: List[Dict], cycle: List[int]) -> bool:
    graph = [_d2obj(e, Edge) for e in g_d]

    if not cycle:
        return True

    adjacency_list = {}
    for edge in graph:
        if edge.src not in adjacency_list:
            adjacency_list[edge.src] = []
        if edge.dest not in adjacency_list:
            adjacency_list[edge.dest] = []
        adjacency_list[edge.src].append(edge.dest)
        adjacency_list[edge.dest].append(edge.src)

    if any([node not in adjacency_list for node in cycle]):
        return False
    # Perform a depth-first search (DFS) to detect cycles
    visited = set()

    def dfs(node, parent):
        visited.add(node)
        for neighbor in adjacency_list.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True
        return False

    # Check if the cycle is present in the graph
    start_node = cycle[0]
    return dfs(start_node, None)


def uf_find(uf_d: Dict, x):
    return _d2obj(uf_d, UnionFind).find(x)
