"""
    __  __  ____   _____   ____         _
|  \/  |/ ___| |_   _| |  _ \  _ __ (_) _ __ ___
| |\/| |\___ \   | |   | |_) || '__|| || '_ ` _ \
| |  | | ___) |  | |   |  __/ | |   | || | | | | |
|_|  |_||____/   |_|   |_|    |_|   |_||_| |_| |_|


Minimal Spanning Tree (using Prim)

This program finds the minimal spanning tree of a non-directed graph using Prim Algorithm.
I.e., the minimal set of edges that enclose all vertices and in which
the sum of the edges' weights is minimal in comparison to any other
subset of the graph's edges.
"""

import sys


class Edge:
    def __init__(self, src, dest, weight):
        self.src = src
        self.dest = dest
        self.weight = weight

    def __repr__(self):
        return f'{self.src}-[{self.weight}]-{self.dest}'


def min_key(key, mst_set):
    min_val = sys.maxsize
    min_index = 0
    for v in range(len(key)):
        if key[v] < min_val and not mst_set[v]:
            min_val = key[v]
            min_index = v
    return min_index


def prim_mst(graph):
    V = len(graph)
    parent = [None] * V  # Initialize parent array with None
    key = [sys.maxsize] * V
    key[0] = 0
    mst_set = [False] * V
    mst = []

    for _ in range(V):
        u = min_key(key, mst_set)
        mst_set[u] = True

        for edge in graph:
            if edge.src == u and not mst_set[edge.dest] and edge.weight < key[edge.dest]:
                parent[edge.dest] = u
                key[edge.dest] = edge.weight

    for i in range(1, len(graph)):
        for edge in graph:
            if edge.dest == i and edge.src == parent[i]:
                mst.append(edge)
                break

    return mst


def print_mst(parent, graph):
    print("Edge \tWeight")
    for i in range(1, len(graph)):
        for edge in graph:
            if edge.dest == i and edge.src == parent[i]:
                print(edge)
                break


def main():
    # Example usage
    graph = [
        Edge(0, 1, 2),
        Edge(0, 3, 6),
        Edge(1, 0, 2),
        Edge(1, 2, 3),
        Edge(1, 3, 8),
        Edge(1, 4, 5),
        Edge(2, 1, 3),
        Edge(2, 4, 7),
        Edge(3, 0, 6),
        Edge(3, 1, 8),
        Edge(3, 4, 9),
        Edge(4, 1, 5),
        Edge(4, 2, 7),
        Edge(4, 3, 9)
    ]

    mst = prim_mst(graph)
    for edge in mst:
        print(edge)


if __name__ == '__main__':
    main()
