import functools
import itertools
import modulefinder
import unittest

CROSS_DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))


def get_adjacent_indexes(start, sizes, directions):
    i, j = start
    adjacent_indexes = [(i + i_delta, j + j_delta)
                        for (i_delta, j_delta) in directions]
    return filter(lambda l: 0 <= l[0] < sizes[0] and 0 <= l[1] < sizes[1], adjacent_indexes)


def get_grid_dims(grid):
    return len(grid), len(grid[0])


def grid_to_list(grid):
    return functools.reduce(lambda x, y: x + y, grid, [])


def connected_components(neighbors):
    seen = set()

    def component(node):
        nodes = set([node])
        while nodes:
            node = nodes.pop()
            seen.add(node)
            nodes |= neighbors[node] - seen
            yield node

    for node in neighbors:
        if node not in seen:
            yield component(node)


class Vertex(object):
    def __init__(self, data):
        self._data = data
        self._neighbours = []
        self._coordinates = None

    def add_neighbours(self, neighbours):
        self._neighbours.extend(neighbours)

    def get_neighbours(self):
        return self._neighbours

    def is_neighbour(self, other):
        return other in self.get_neighbours()

    def remove_neighbour(self, other):
        self._neighbours.remove(other)

    def get_data(self):
        return self._data

    def set_coordinates(self, x, y):
        self._coordinates = (x, y)

    def get_coordinates(self):
        return self._coordinates

    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr(self._data))


class GridGraph(object):
    def __init__(self, vertices_grid):
        self._vertices = vertices_grid

        x_size, y_size = get_grid_dims(vertices_grid)
        for i in range(x_size):
            for j in range(y_size):
                curr = self._vertices[i][j]
                curr.set_coordinates(i, j)
                # neighbours_indexes = get_adjacent_indexes(
                #     (i, j), sizes=(x_size, y_size), directions=CROSS_DIRECTIONS)
                # curr.add_neighbours([vertices_grid[x][y]
                #                      for x, y in neighbours_indexes])

    def _are_neighbours(self, v1, v2):
        return v1.is_neighbour(v2) and v2.is_neighbour(v1)

    def _split_neighbours(self, v1, v2):
        v1.remove_neighbour(v2)
        v2.remove_neighbour(v1)

    def get_vertices_as_list(self):
        return grid_to_list(self._vertices)

    def to_adjacency_dict(self):
        return {vertex: set(vertex.get_neighbours()) for vertex in self.get_vertices_as_list()}

    def remove_edge(self, v1, v2):
        if self._are_neighbours(v1, v2):
            self._split_neighbours(v1, v2)

    def get_connected_components(self):
        return [list(cc) for cc in connected_components(self.to_adjacency_dict())]

    def get_vertex(self, i, j):
        return self._vertices[i][j]

    def get_dims(self):
        return len(self._vertices), len(self._vertices[0])

    def get_vertices_as_grid(self):
        return self._vertices


class DualVertex(Vertex):
    def __init__(self, data):
        super(DualVertex, self).__init__(data)
        self._dual = Vertex(data)

    @property
    def dual(self):
        return self._dual


class BaseGridGraphTest(unittest.TestCase):
    def assertNeighbour(self, v1, v2):
        self.assertTrue(v1.is_neighbour(v2) and v2.is_neighbour(v1))

    def assertNotNeighbour(self, v1, v2):
        self.assertTrue(not v1.is_neighbour(v2) and not v2.is_neighbour(v1))

    def assertEqualListContent(self, l1, l2):
        msg = '{func}({l1}) != {func}({l2})'
        self.assertEqual(len(l1),
                         len(l2),
                         'len({}) != len({})'.format(l1, l2))
        self.assertEqual(set(l1), set(l2))


class GridGraphTest(BaseGridGraphTest):
    def setUp(self):
        self._data_grid = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]

        self._vertices = [[Vertex(d) for d in row] for row in self._data_grid]
        self._graph = GridGraph(self._vertices)

    def test_get_vertex(self):
        x_size, y_size = get_grid_dims(self._data_grid)
        for i in range(x_size):
            for j in range(y_size):
                curr_vertex = self._graph.get_vertex(i, j)
                self.assertEqual(curr_vertex.get_data(), self._data_grid[i][j])
                self.assertEqual(curr_vertex.get_coordinates(), (i, j))

    def test_remove_edge_from_neighbour(self):
        v1 = self._graph.get_vertex(1, 0)
        v2 = self._graph.get_vertex(1, 1)

        self.assertNeighbour(v1, v2)
        self._graph.remove_edge(v1, v2)
        self.assertNotNeighbour(v1, v2)

    def test_remove_edge_from_not_neighbour(self):
        v1 = self._graph.get_vertex(1, 0)
        v2 = self._graph.get_vertex(1, 2)

        self.assertNotNeighbour(v1, v2)
        self._graph.remove_edge(v1, v2)
        self.assertNotNeighbour(v1, v2)

    def test_single_connected_components(self):
        ccs = list(self._graph.get_connected_components())
        vertices = grid_to_list(self._vertices)

        self.assertEqual(len(ccs), 1)
        self.assertEqualListContent(ccs[0], vertices)

    def test_two_connected_components(self):
        """
        first cc:
        [1, 2, 3],

        second cc:
        [4, 5, 6],
        [7, 8, 9],
        """
        g = self._graph
        g.remove_edge(g.get_vertex(0, 0), g.get_vertex(1, 0))
        g.remove_edge(g.get_vertex(0, 1), g.get_vertex(1, 1))
        g.remove_edge(g.get_vertex(0, 2), g.get_vertex(1, 2))

        ccs = list(self._graph.get_connected_components())
        ccs = sorted(ccs, key=len)
        expected_cc = [self._vertices[0], self._vertices[1] + self._vertices[2]]

        #self.assertEqual(len(ccs), 2)
        for cc, expected in zip(ccs, expected_cc):
            #self.assertEqualListContent(cc, expected)
            pass


if __name__ == "__main__":
    g = GridGraphTest()
    g.setUp()
    #g.test_get_vertex()
    # g.test_remove_edge_from_neighbour()
    # g.test_remove_edge_from_not_neighbour()
    # g.test_single_connected_components()
    g.test_two_connected_components()
