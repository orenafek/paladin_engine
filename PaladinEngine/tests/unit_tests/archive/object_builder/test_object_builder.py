import unittest
from abc import ABC
from collections import deque
from itertools import chain
from pathlib import Path
from typing import *

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, Identifier, AttributedDict
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from archive.object_builder.naive_object_builder.naive_object_builder import NaiveObjectBuilder
from tests.test_common.test_common import TestCommon, SKIP_VALUE
from utils.utils import separate_line_no


class TestObjectBuilder(TestCommon, ABC):
    def setUp(self) -> None:
        self.object_builder = DiffObjectBuilder(self.archive)

    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        return self.object_builder._build_iterator(obj, line_no)

    def _test_series_of_values(self, obj: Identifier, *expected: Any):
        obj, line_no = separate_line_no(obj)
        return self._test_series(obj, lambda value: value, line_no, *expected)


def setUpDiff(self):
    self.object_builder = DiffObjectBuilder(self.archive)


def setUpNaive(self):
    self.object_builder = NaiveObjectBuilder(self.archive)


class TestNestedObjectBuild(TestObjectBuilder, ABC):
    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic2')

    def test_object_name(self):
        self._test_series_of_values('r0',
                                    SKIP_VALUE,
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': -1, '_y': -2}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 0, '_y': 1}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 1, '_y': 2}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 2, '_y': 3}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 4, '_y': 4}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 1, '_y': 2}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 9, '_y': 2}},
                                    )

    def test_field_access(self):
        self._test_series('r0',
                          lambda value: eval('r0.rt', {'r0': value}) if value is not None else None,
                          -1,
                          SKIP_VALUE,
                          {'_x': 3, '_y': 4},
                          {'_x': -1, '_y': -2},
                          {'_x': 0, '_y': 1},
                          {'_x': 1, '_y': 2},
                          {'_x': 2, '_y': 3},
                          {'_x': 3, '_y': 4},
                          {'_x': 4, '_y': 4},
                          {'_x': 1, '_y': 2},
                          {'_x': 9, '_y': 2})



class TestNestedObjectBuildNaive(TestNestedObjectBuild):
    setUp = setUpNaive


class TestBuiltinCollections(TestObjectBuilder, ABC):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic3')

    def test_lists(self):
        self._test_series_of_values('l1', None, [1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6], [1, 2, 4, 5, 6], [6, 5, 4, 2, 1],
                                    [], [6, 7, 8, 9, 10])

    def tests_deques(self):
        self._test_series_of_values('dq', None, *[deque(l) for l in
                                                  [['a', 'b', 'c', 'd', 'e'],
                                                   ['a', 'b', 'c', 'd', 'e', 'f'],
                                                   ['~', 'a', 'b', 'c', 'd', 'e', 'f'],
                                                   ['~', 'a', 'b', 'd', 'e', 'f'],
                                                   ['f', 'e', 'd', 'b', 'a', '~'],
                                                   [],
                                                   ['g', 'h', 'i', 'j', 'k'],
                                                   ['c', 'b', 'a', 'g', 'h', 'i', 'j', 'k'],
                                                   ['b', 'a', 'g', 'h', 'i', 'j', 'k']
                                                   ]])

    def test_sets(self):
        self._test_series_of_values('s1', None, {1, 2, 3}, {1, 2, 3, 4}, {2, 3, 4}, {2, 3, 4, 5}, {2, 3, 4}, {2, 4},
                                    {1, 2, 3, 4, 5}, {3, 4, 5}, {3, 4, 6, 7}, set())

    def test_tuples(self):
        self._test_series_of_values('t1', None, (1, 2, 3,))

    def test_dicts(self):
        self._test_series_of_values('d1', None, {1: 'a', 2: 'b', 3: 'c'})
        self._test_series_of_values('d2', SKIP_VALUE,
                                    {AttributedDict([('value', 'A')]): 1,
                                     AttributedDict([('value', 'B')]): 2})
        self._test_series_of_values('d3', SKIP_VALUE,
                                    {AttributedDict([('A', 1), ('B', 2)]): 3})


class TestBuiltinCollectionsNaive(TestBuiltinCollections):
    setUp = setUpNaive


class TestGraph(TestObjectBuilder, ABC):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('graphs')

    # @pytest.mark.skip(reason='')
    def test_g(self):
        vertex = lambda val: AttributedDict({'value': val})
        edge = lambda f, t, w: AttributedDict({'v_from': vertex(f), 'v_to': vertex(t), 'weight': w})
        graph = lambda v, e: AttributedDict({'vertices': v, 'edges': e})

        self._test_series_of_values('g',
                                    SKIP_VALUE,
                                    graph(set(), set()),
                                    graph({vertex('A')}, set()),
                                    SKIP_VALUE,
                                    graph({vertex('A'), vertex('B')}, {edge('A', 'B', 1)}),
                                    SKIP_VALUE,
                                    graph({vertex('A'), vertex('B'), vertex('C')},
                                          {edge('A', 'B', 1), edge('B', 'C', 2)}),
                                    SKIP_VALUE
                                    )


@unittest.skip(reason='Way too much time...')
class TestGraphNaive(TestGraph):
    setUp = setUpNaive


class TestBasic4(TestObjectBuilder, ABC):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic4')

    def test_same_name_multiple_line_no(self):
        self._test_series_of_values('i@2', SKIP_VALUE, *range(5), None)
        self._test_series_of_values('i@7', SKIP_VALUE, *range(5, 11), None)

    def test_function_call_ret_value(self):
        self._test_series_of_values(f'square',
                                    SKIP_VALUE,
                                    *list(
                                        chain.from_iterable((value, None) for value in [x * x for x in range(1, 11)])))


class TestBasic4Naive(TestBasic4):
    setUp = setUpNaive


class TestCaterpillar(TestObjectBuilder, ABC):
    @classmethod
    def program_path(cls) -> Path:
        return cls.example('caterpillar')

    def test_same_names_multiple_line_no(self):
        self._test_series_of_values('i@13', None, *range(0, 5), None)
        self._test_series_of_values('total_slices@12', None, *range(0, 12), None)


class TestCaterpillarNaive(TestCaterpillar):
    setUp = setUpNaive
