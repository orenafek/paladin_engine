from stubs.stubs import __FLI__, __POST_CONDITION__, __FC__, __AS__, __FRAME__, __ARG__, __DEF__, __UNDEF__, __AC__, __PIS__, __PALADIN_LIST__, __BREAK__, __SOLI__, __EOLI__, __BMFCS__, __PRINT__


from dataclasses import dataclass, field
from functools import reduce
from math import inf
from typing import Optional, Set, Tuple, Iterable, Union, Dict, List

@dataclass
class Vertex(object):
    value: object

    def __eq__(self, other):
        __DEF__('__eq__', 11, frame=__FRAME__())
        __ARG__('__eq__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=11)
        __ARG__('__eq__', 'other', other, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=11)
        __UNDEF__('__eq__', line_no=11, frame=__FRAME__())
        return __FC__('isinstance(other, Vertex)', isinstance, locals(), globals(), __FRAME__(), 12, other, Vertex) and self.value == other.value

    def __hash__(self):
        __DEF__('__hash__', 11, frame=__FRAME__())
        __ARG__('__hash__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=11)
        __UNDEF__('__hash__', line_no=11, frame=__FRAME__())
        return __FC__('hash(self.value)', hash, locals(), globals(), __FRAME__(), 15, self.value)

    def __repr__(self):
        __DEF__('__repr__', 11, frame=__FRAME__())
        __ARG__('__repr__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=11)
        __UNDEF__('__repr__', line_no=11, frame=__FRAME__())
        return __FC__('str(self.value)', str, locals(), globals(), __FRAME__(), 18, self.value)

@dataclass
class DirectedEdge(object):
    v_from: Vertex
    v_to: Vertex
    weight: Optional[int] = __FC__('field(default=-1)', field, locals(), globals(), __FRAME__(), 25, default=-1)

    def __eq__(self, other):
        __DEF__('__eq__', 27, frame=__FRAME__())
        __ARG__('__eq__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=27)
        __ARG__('__eq__', 'other', other, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=27)
        __UNDEF__('__eq__', line_no=27, frame=__FRAME__())
        return __FC__('isinstance(other, DirectedEdge)', isinstance, locals(), globals(), __FRAME__(), 28, other, DirectedEdge) and self.v_from == other.v_from and (self.v_to == other.v_to)

    def __hash__(self):
        __DEF__('__hash__', 27, frame=__FRAME__())
        __ARG__('__hash__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=27)
        __UNDEF__('__hash__', line_no=27, frame=__FRAME__())
        return __FC__("hash(__FC__('hash(self.v_from)', hash, locals(), globals(), __FRAME__(), 31, self.v_from) + __FC__('hash(self.v_to)', hash, locals(), globals(), __FRAME__(), 31, self.v_to))", hash, locals(), globals(), __FRAME__(), 31, __FC__('hash(self.v_from)', hash, locals(), globals(), __FRAME__(), 31, self.v_from) + __FC__('hash(self.v_to)', hash, locals(), globals(), __FRAME__(), 31, self.v_to))

    def __repr__(self):
        __DEF__('__repr__', 27, frame=__FRAME__())
        __ARG__('__repr__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=27)
        __UNDEF__('__repr__', line_no=27, frame=__FRAME__())
        return f'{self.v_from} -[{self.weight}]-> {self.v_to}'

@dataclass
class DirectedGraph(object):

    def __init__(self):
        __DEF__('__init__', 47, frame=__FRAME__())
        __PIS__(self, 'self', 47)
        __ARG__('__init__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        self.vertices = __FC__('set()', set, locals(), globals(), __FRAME__(), 41)
        __AS__('self.vertices = __FC__(@set()@, set, locals(), globals(), __FRAME__(), 41)', 'self.vertices', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=41)
        self.edges = __FC__('set()', set, locals(), globals(), __FRAME__(), 42)
        __AS__('self.edges = __FC__(@set()@, set, locals(), globals(), __FRAME__(), 42)', 'self.edges', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=42)
        __UNDEF__('__init__', line_no=47, frame=__FRAME__())
        return None
    KEY_NOT_IN_EDGE_FORMAT = __FC__("TypeError('key should by in the format of (V, V)')", TypeError, locals(), globals(), __FRAME__(), 47, 'key should by in the format of (V, V)')
    __AS__('KEY_NOT_IN_EDGE_FORMAT = __FC__(@TypeError(@key should by in the format of (V, V)@)@, TypeError, locals(), globals(), __FRAME__(), 47, @key should by in the format of (V, V)@)', 'KEY_NOT_IN_EDGE_FORMAT', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)

    @staticmethod
    def _is_edge_key(key: object):
        __DEF__('_is_edge_key', 47, frame=__FRAME__())
        __ARG__('_is_edge_key', 'key', key, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __UNDEF__('_is_edge_key', line_no=47, frame=__FRAME__())
        return __FC__('isinstance(key, Tuple)', isinstance, locals(), globals(), __FRAME__(), 51, key, Tuple) and __FC__('len(key)', len, locals(), globals(), __FRAME__(), 51, key) == 2

    def __len__(self):
        __DEF__('__len__', 47, frame=__FRAME__())
        __ARG__('__len__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __UNDEF__('__len__', line_no=47, frame=__FRAME__())
        return __FC__('len(self.vertices)', len, locals(), globals(), __FRAME__(), 54, self.vertices)

    def __getitem__(self, item) -> Optional[Union[Iterable[Vertex], int]]:
        __DEF__('__getitem__', 47, frame=__FRAME__())
        __ARG__('__getitem__', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('__getitem__', 'item', item, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        if __FC__('isinstance(item, Vertex)', isinstance, locals(), globals(), __FRAME__(), 57, item, Vertex):
            if item not in self.vertices:
                __UNDEF__('__getitem__', line_no=47, frame=__FRAME__())
                return []
            __UNDEF__('__getitem__', line_no=47, frame=__FRAME__())
            return [e.v_to for e in __FC__('filter(lambda e: e.v_from == item, self.edges)', filter, locals(), globals(), __FRAME__(), 61, lambda e: e.v_from == item, self.edges)]
        if not __FC__('DirectedGraph._is_edge_key(item)', DirectedGraph._is_edge_key, locals(), globals(), __FRAME__(), 63, item):
            raise DirectedGraph.KEY_NOT_IN_EDGE_FORMAT
        e = __FC__('self._find_edge(item)', self._find_edge, locals(), globals(), __FRAME__(), 66, item)
        __AS__('e = __FC__(@self._find_edge(item)@, self._find_edge, locals(), globals(), __FRAME__(), 66, item)', 'e', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=66)
        if not e:
            __UNDEF__('__getitem__', line_no=47, frame=__FRAME__())
            return None
        __UNDEF__('__getitem__', line_no=47, frame=__FRAME__())
        return e.weight

    def add_edge(self, _from: object, to: object, weight: int):
        __DEF__('add_edge', 47, frame=__FRAME__())
        __ARG__('add_edge', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('add_edge', '_from', _from, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('add_edge', 'to', to, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('add_edge', 'weight', weight, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        v_from = __FC__('Vertex(_from)', Vertex, locals(), globals(), __FRAME__(), 73, _from)
        __AS__('v_from = __FC__(@Vertex(_from)@, Vertex, locals(), globals(), __FRAME__(), 73, _from)', 'v_from', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=73)
        v_to = __FC__('Vertex(to)', Vertex, locals(), globals(), __FRAME__(), 74, to)
        __AS__('v_to = __FC__(@Vertex(to)@, Vertex, locals(), globals(), __FRAME__(), 74, to)', 'v_to', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=74)
        __BMFCS__(__FC__('self.vertices.add(v_from)', self.vertices.add, locals(), globals(), __FRAME__(), 76, v_from), self.vertices, 'self.vertices', 'add', 76, v_from, __FRAME__(), locals(), globals())
        __BMFCS__(__FC__('self.vertices.add(v_to)', self.vertices.add, locals(), globals(), __FRAME__(), 77, v_to), self.vertices, 'self.vertices', 'add', 77, v_to, __FRAME__(), locals(), globals())
        e = __FC__('self._find_edge((v_from, v_to))', self._find_edge, locals(), globals(), __FRAME__(), 79, (v_from, v_to))
        __AS__('e = __FC__(@self._find_edge((v_from, v_to))@, self._find_edge, locals(), globals(), __FRAME__(), 79, (v_from, v_to))', 'e', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=79)
        if e:
            e.weight = weight
            __AS__('e.weight = weight', 'e.weight', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=82)
        else:
            __BMFCS__(__FC__('self.edges.add(DirectedEdge(v_from, v_to, weight))', self.edges.add, locals(), globals(), __FRAME__(), 84, DirectedEdge(v_from, v_to, weight)), self.edges, 'self.edges', 'add', 84, __FC__('DirectedEdge(v_from, v_to, weight)', DirectedEdge, locals(), globals(), __FRAME__(), 84, v_from, v_to, weight), __FRAME__(), locals(), globals())
        __UNDEF__('add_edge', line_no=47, frame=__FRAME__())
        return None

    def _find_edge(self, key: Tuple[Vertex, Vertex]) -> Optional[DirectedEdge]:
        __DEF__('_find_edge', 47, frame=__FRAME__())
        __ARG__('_find_edge', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('_find_edge', 'key', key, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        for __iter_4 in self.edges:
            __SOLI__(87, __FRAME__())
            e = __iter_4
            __AS__('e = __iter_4', 'e', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=87)
            if e.v_from == key[0] and e.v_to == key[1]:
                __UNDEF__('_find_edge', line_no=47, frame=__FRAME__())
                return e
            __EOLI__(__FRAME__(), loop_start_line_no=87, loop_end_line_no=89)
        __UNDEF__('_find_edge', line_no=47, frame=__FRAME__())
        return None

    def _find_connected(self, v: Vertex) -> Set[Vertex]:
        __DEF__('_find_connected', 47, frame=__FRAME__())
        __ARG__('_find_connected', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('_find_connected', 'v', v, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __UNDEF__('_find_connected', line_no=47, frame=__FRAME__())
        return __FC__("set(map(lambda e: e.v_to, __FC__('filter(lambda e: e.v_from == v, self.edges)', filter, locals(), globals(), __FRAME__(), 92, lambda e: e.v_from == v, self.edges)))", set, locals(), globals(), __FRAME__(), 92, map(lambda e: e.v_to, __FC__('filter(lambda e: e.v_from == v, self.edges)', filter, locals(), globals(), __FRAME__(), 92, lambda e: e.v_from == v, self.edges)))

    @property
    def _have_parents(self):
        __DEF__('_have_parents', 47, frame=__FRAME__())
        __ARG__('_have_parents', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __UNDEF__('_have_parents', line_no=47, frame=__FRAME__())
        return __FC__('self.vertices.difference(self._roots)', self.vertices.difference, locals(), globals(), __FRAME__(), 96, self._roots)

    @property
    def _roots(self) -> Set[Vertex]:
        __DEF__('_roots', 47, frame=__FRAME__())
        __ARG__('_roots', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __UNDEF__('_roots', line_no=47, frame=__FRAME__())
        return __FC__("self.vertices.difference(set(__FC__('map(lambda e: e.v_to, self.edges)', map, locals(), globals(), __FRAME__(), 100, lambda e: e.v_to, self.edges)))", self.vertices.difference, locals(), globals(), __FRAME__(), 100, set(__FC__('map(lambda e: e.v_to, self.edges)', map, locals(), globals(), __FRAME__(), 100, lambda e: e.v_to, self.edges)))

    def _find_vertex(self, value: object) -> Optional[Vertex]:
        __DEF__('_find_vertex', 47, frame=__FRAME__())
        __ARG__('_find_vertex', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('_find_vertex', 'value', value, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        found = [v for v in self.vertices if v.value == value]
        __AS__('found = [v for v in self.vertices if v.value == value]', 'found', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=103)
        if __FC__('len(found)', len, locals(), globals(), __FRAME__(), 104, found) != 1:
            __UNDEF__('_find_vertex', line_no=47, frame=__FRAME__())
            return None
        __UNDEF__('_find_vertex', line_no=47, frame=__FRAME__())
        return found[0]

    def pre_order(self) -> Iterable[Vertex]:
        __DEF__('pre_order', 47, frame=__FRAME__())
        __ARG__('pre_order', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        order = []
        __AS__('order = []', 'order', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=110)
        roots = self._roots
        __AS__('roots = self._roots', 'roots', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=111)
        while roots:
            __SOLI__(113, __FRAME__())
            __BMFCS__(__FC__('order.extend(roots)', order.extend, locals(), globals(), __FRAME__(), 114, roots), order, 'order', 'extend', 114, roots, __FRAME__(), locals(), globals())
            roots = __FC__("reduce(lambda rr, r: __FC__('rr.union(r)', rr.union, locals(), globals(), __FRAME__(), 115, r), map(lambda r: __FC__('self._find_connected(r)', self._find_connected, locals(), globals(), __FRAME__(), 115, r), roots), set())", reduce, locals(), globals(), __FRAME__(), 115, lambda rr, r: __FC__('rr.union(r)', rr.union, locals(), globals(), __FRAME__(), 115, r), map(lambda r: __FC__('self._find_connected(r)', self._find_connected, locals(), globals(), __FRAME__(), 115, r), roots), set())
            __AS__('roots = __FC__(@reduce(lambda rr, r: __FC__(@rr.union(r)@, rr.union, locals(), globals(), __FRAME__(), 115, r), map(lambda r: __FC__(@self._find_connected(r)@, self._find_connected, locals(), globals(), __FRAME__(), 115, r), roots), set())@, reduce, locals(), globals(), __FRAME__(), 115, lambda rr, r: __FC__(@rr.union(r)@, rr.union, locals(), globals(), __FRAME__(), 115, r), map(lambda r: __FC__(@self._find_connected(r)@, self._find_connected, locals(), globals(), __FRAME__(), 115, r), roots), set())', 'roots', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=115)
            __EOLI__(__FRAME__(), loop_start_line_no=113, loop_end_line_no=115)
        __UNDEF__('pre_order', line_no=47, frame=__FRAME__())
        return order

    def shortest_path(self, _from: object, _to: object):
        __DEF__('shortest_path', 47, frame=__FRAME__())
        __ARG__('shortest_path', 'self', self, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('shortest_path', '_from', _from, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        __ARG__('shortest_path', '_to', _to, locals=locals(), globals=globals(), frame=__FRAME__(), line_no=47)
        v_from = __FC__('self._find_vertex(_from)', self._find_vertex, locals(), globals(), __FRAME__(), 121, _from)
        __AS__('v_from = __FC__(@self._find_vertex(_from)@, self._find_vertex, locals(), globals(), __FRAME__(), 121, _from)', 'v_from', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=121)
        v_to = __FC__('self._find_vertex(_to)', self._find_vertex, locals(), globals(), __FRAME__(), 122, _to)
        __AS__('v_to = __FC__(@self._find_vertex(_to)@, self._find_vertex, locals(), globals(), __FRAME__(), 122, _to)', 'v_to', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=122)
        if not v_from or not v_to:
            __UNDEF__('shortest_path', line_no=47, frame=__FRAME__())
            return []
        distances: Dict[Vertex, Union[int, float]] = {v: inf for v in self.vertices}
        distances[v_from] = 0
        __AS__('distances[v_from] = 0', 'distances[v_from]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=127)
        unvisited: Set[Vertex] = {v for v in self.vertices}
        prev: Dict[Vertex, Vertex] = {}
        current: Optional[Vertex] = None
        while unvisited:
            __SOLI__(133, __FRAME__())
            current: Vertex = __FC__('sorted(distances.items(), key=lambda t: t[1])', sorted, locals(), globals(), __FRAME__(), 134, distances.items(), key=lambda t: t[1])[0][0]
            if current == v_to:
                __BREAK__(frame=__FRAME__(), line_no=136)
                break
            __BMFCS__(__FC__('unvisited.remove(current)', unvisited.remove, locals(), globals(), __FRAME__(), 137, current), unvisited, 'unvisited', 'remove', 137, current, __FRAME__(), locals(), globals())
            neighbors = __FC__('self._find_connected(current)', self._find_connected, locals(), globals(), __FRAME__(), 138, current)
            __AS__('neighbors = __FC__(@self._find_connected(current)@, self._find_connected, locals(), globals(), __FRAME__(), 138, current)', 'neighbors', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=138)
            for __iter_0 in __FC__('neighbors.union(unvisited)', neighbors.union, locals(), globals(), __FRAME__(), 139, unvisited):
                __SOLI__(139, __FRAME__())
                neighbor = __iter_0
                __AS__('neighbor = __iter_0', 'neighbor', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=139)
                d = distances[current] + __FC__('self._find_edge((current, neighbor))', self._find_edge, locals(), globals(), __FRAME__(), 140, (current, neighbor)).weight
                __AS__('d = distances[current] + __FC__(@self._find_edge((current, neighbor))@, self._find_edge, locals(), globals(), __FRAME__(), 140, (current, neighbor)).weight', 'd', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=140)
                if d < distances[neighbor]:
                    distances[neighbor] = d
                    __AS__('distances[neighbor] = d', 'distances[neighbor]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=142)
                    prev[neighbor] = current
                    __AS__('prev[neighbor] = current', 'prev[neighbor]', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=143)
                __EOLI__(__FRAME__(), loop_start_line_no=139, loop_end_line_no=143)
            __EOLI__(__FRAME__(), loop_start_line_no=133, loop_end_line_no=143)
        if current != v_to:
            __UNDEF__('shortest_path', line_no=47, frame=__FRAME__())
            return []
        rev_path: List[Vertex] = []
        current = v_to
        __AS__('current = v_to', 'current', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=149)
        while prev:
            __SOLI__(150, __FRAME__())
            __BMFCS__(__FC__('rev_path.append(current)', rev_path.append, locals(), globals(), __FRAME__(), 151, current), rev_path, 'rev_path', 'append', 151, current, __FRAME__(), locals(), globals())
            current = prev[current]
            __AS__('current = prev[current]', 'current', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=152)
            __FC__('prev.pop(current)', prev.pop, locals(), globals(), __FRAME__(), 153, current)
            __EOLI__(__FRAME__(), loop_start_line_no=150, loop_end_line_no=153)
        __UNDEF__('shortest_path', line_no=47, frame=__FRAME__())
        return __FC__('reversed(rev_path)', reversed, locals(), globals(), __FRAME__(), 155, rev_path)

def main():
    __DEF__('main', 157, frame=__FRAME__())
    g = __FC__('DirectedGraph()', DirectedGraph, locals(), globals(), __FRAME__(), 158)
    __AS__('g = __FC__(@DirectedGraph()@, DirectedGraph, locals(), globals(), __FRAME__(), 158)', 'g', locals=locals(), globals=globals(), frame=__FRAME__(), line_no=158)
    __FC__("g.add_edge('A', 'B', 1)", g.add_edge, locals(), globals(), __FRAME__(), 170, 'A', 'B', 1)
    __FC__("g.add_edge('B', 'C', 2)", g.add_edge, locals(), globals(), __FRAME__(), 171, 'B', 'C', 2)
    __FC__("g.add_edge('C', 'D', 3)", g.add_edge, locals(), globals(), __FRAME__(), 172, 'C', 'D', 3)
    __PRINT__(174, __FRAME__(), f'Vertices: {g.vertices}')
    __PRINT__(175, __FRAME__(), f"Pre Order: {__FC__('g.pre_order()', g.pre_order, locals(), globals(), __FRAME__(), 175)}")
    __UNDEF__('main', line_no=157, frame=__FRAME__())
    return None
if __name__ == '__main__':
    __FC__('main()', main, locals(), globals(), __FRAME__(), 180)