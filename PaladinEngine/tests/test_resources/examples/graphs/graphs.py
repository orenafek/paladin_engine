from functools import reduce
from math import inf
from typing import Optional, Set, Tuple, Iterable, Union, Dict, List


class Vertex(object):
    def __init__(self, value):
        self.value: object = value

    def __eq__(self, other):
        return isinstance(other, Vertex) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f'"{str(self.value)}"'


class DirectedEdge(object):

    def __init__(self, v_from, v_to, weight: int = -1):
        self.v_from: Vertex = v_from
        self.v_to: Vertex = v_to
        self.weight: int = weight

    def __eq__(self, other):
        return isinstance(other, DirectedEdge) and self.v_from == other.v_from and self.v_to == other.v_to

    def __hash__(self):
        return hash(hash(self.v_from) + hash(self.v_to))

    def __repr__(self):
        return f'{self.v_from} -[{self.weight}]-> {self.v_to}'


class DirectedGraph(object):

    def __init__(self):
        self.vertices = set()
        self.edges = set()

    KEY_NOT_IN_EDGE_FORMAT = TypeError('key should by in the format of (V, V)')

    @staticmethod
    def _is_edge_key(key: object):
        return isinstance(key, Tuple) and len(key) == 2  # and isinstance(key[0], Vertex) and isinstance(key[1], Vertex)

    def __len__(self):
        return len(self.vertices)

    def __getitem__(self, item) -> Optional[Union[Iterable[Vertex], int]]:
        if isinstance(item, Vertex):
            if item not in self.vertices:
                return []

            return [e.v_to for e in filter(lambda e: e.v_from == item, self.edges)]

        if not DirectedGraph._is_edge_key(item):
            raise DirectedGraph.KEY_NOT_IN_EDGE_FORMAT

        e = self._find_edge(item)
        if not e:
            return None

        return e.weight

    def __repr__(self):
        return '{' + f'{[self.vertices]}' + '}'

    def add_edge(self, _from: object, to: object, weight: int):
        v_from = Vertex(_from)
        v_to = Vertex(to)

        self.vertices.add(v_from)
        self.vertices.add(v_to)

        self.edges.add(DirectedEdge(v_from, v_to, weight))

    def _find_edge(self, key: Tuple[Vertex, Vertex]) -> Optional[DirectedEdge]:
        for e in self.edges:
            if e.v_from == key[0] and e.v_to == key[1]:
                return e

    def _find_connected(self, v: Vertex) -> Set[Vertex]:
        return set(map(lambda e: e.v_to, filter(lambda e: e.v_from == v, self.edges)))

    @property
    def _have_parents(self):
        return self.vertices.difference(self._roots)

    @property
    def _roots(self) -> Set[Vertex]:
        return self.vertices.difference(set(map(lambda e: e.v_to, self.edges)))

    def _find_vertex(self, value: object) -> Optional[Vertex]:
        found = [v for v in self.vertices if v.value == value]
        if len(found) != 1:
            return None

        return found[0]

    def pre_order(self) -> Iterable[Vertex]:
        order = []
        roots = self._roots

        while roots:
            order.extend(roots)
            roots = reduce(lambda rr, r: rr.union(r), map(lambda r: self._find_connected(r), roots), set())

        return order

    def shortest_path(self, _from: object, _to: object):

        v_from = self._find_vertex(_from)
        v_to = self._find_vertex(_to)
        if not v_from or not v_to:
            return []

        distances: Dict[Vertex, Union[int, float]] = {v: inf for v in self.vertices}
        distances[v_from] = 0

        unvisited: Set[Vertex] = {v for v in self.vertices}
        prev: Dict[Vertex, Vertex] = {}

        current: Optional[Vertex] = None
        while unvisited:
            current: Vertex = sorted(distances.items(), key=lambda t: t[1])[0][0]
            if current == v_to:
                break
            unvisited.remove(current)
            neighbors = self._find_connected(current)
            for neighbor in neighbors.intersection(unvisited):
                print(f'fe = {self._find_edge((current, neighbor))}')
                e = self._find_edge((current, neighbor))
                d = distances[current] + e.weight
                if d < distances[neighbor]:
                    distances[neighbor] = d
                    prev[neighbor] = current
            del distances[current]

        if current != v_to:
            return []

        path: List[Vertex] = []
        current = v_to
        while current != v_from:
            path.append(current)
            current = prev[current]

        path = [v_from] + list(reversed(path))
        dist = sum([self._find_edge((f, t)).weight for f, t in zip(path, path[1::])])

        return path, dist


def main():
    g = DirectedGraph()

    g.add_edge('A', 'B', 1)
    g.add_edge('B', 'C', 2)
    g.add_edge('C', 'D', 3)
    print(f'Vertices: {g.vertices}')
    print(f'Pre Order: {g.pre_order()}')

    g1 = DirectedGraph()
    g1.add_edge('A', 'B', 1)
    g1.add_edge('B', 'E', 8)
    g1.add_edge('E', 'G', 7)
    g1.add_edge('B', 'F', 9)
    g1.add_edge('F', 'C', 3)
    g1.add_edge('C', 'D', 5)
    g1.add_edge('D', 'G', 6)
    g1.add_edge('C', 'G', 4)
    g1.add_edge('A', 'C', 2)
    print(g1.edges)
    a_g_path, a_g_dist = g1.shortest_path("A", "G")
    print(f'Shortest Path of A->G: {a_g_path}, dist: {a_g_dist}')


if __name__ == '__main__':
    main()
