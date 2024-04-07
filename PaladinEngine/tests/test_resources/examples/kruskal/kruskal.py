import itertools

from stubs.stubs import archive, __PAUSE__, __RESUME__


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
            if self.rank[root_x] == self.rank[root_y]:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            else:
                self.parent[root_y] = root_y  # BUG



class Edge:
    def __init__(self, src, dest, weight):
        self.src = src
        self.dest = dest
        self.weight = weight

    def __repr__(self):
        return f'{self.src}-[{self.weight}]-{self.dest}'


def kruskal(graph, num_vertices):
    sorted_edges = sorted(graph, key=lambda e: e.weight)
    mst = []
    uf = UnionFind(num_vertices)

    for edge in sorted_edges:
        src = edge.src
        dest = edge.dest
        uff_s = uf.find(src)
        uff_d = uf.find(dest)
        if uff_s != uff_d:
            uf.union(src, dest)
            mst.append(edge)

    return mst


def find_all_spanning_trees(graph, num_vertices):
    all_trees = []

    # Generate all possible combinations of edges
    for r in range(num_vertices - 1, len(graph)):
        for edges in itertools.combinations(graph, r):
            uf = UnionFind(num_vertices)
            tree = list(edges)

            # Add remaining edges to form a spanning tree
            for edge in graph:
                if len(tree) == num_vertices - 1:
                    break
                if edge not in tree and uf.find(edge.src) != uf.find(edge.dest):
                    tree.append(edge)
                    uf.union(edge.src, edge.dest)

            # Check if the tree spans all vertices
            if len(tree) == num_vertices - 1:
                all_trees.append(tree)

    return all_trees


def st_weight(st):
    return sum([e.weight for e in st])


# Example usage
if __name__ == "__main__":
    # Example graph represented as a list of edges
    graph = [
             Edge(0, 1, 9),
             Edge(2, 0, 6),
             Edge(0, 3, 2),
             Edge(1, 2, 7),
             Edge(3, 1, 6),
             Edge(2, 3, 8),
          ]

    # Number of vertices in the graph
    num_vertices = 4

    # Find the minimum spanning tree
    mst = kruskal(graph, num_vertices)
    mst_weight = st_weight(mst)

#    __PAUSE__()
    all_st = find_all_spanning_trees(graph, num_vertices)
#    __RESUME__()
    min_st_weight = min([st_weight(st) for st in all_st])

    if min_st_weight < mst_weight:
        raise RuntimeError(f"weight(minimal st)[{min_st_weight}] < weight(found mst)[{mst_weight}]")
