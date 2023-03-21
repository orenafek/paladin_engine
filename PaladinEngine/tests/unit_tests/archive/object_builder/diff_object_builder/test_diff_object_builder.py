import unittest
from abc import abstractmethod, ABC
from pathlib import Path
from typing import *

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import ObjectId, LineNo, Time
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import SCOPE_SIGN
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from tests.test_common.test_common import TestCommon, SKIP_VALUE


class TestDiffObjectBuilder(TestCommon, ABC):
    def setUp(self) -> None:
        self.diff_object_builder = DiffObjectBuilder(self.archive)

    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        return self.diff_object_builder._build_iterator(obj, line_no)

    @staticmethod
    def _separate_line_no(obj: Union[str, ObjectId]):
        if isinstance(obj, str) and SCOPE_SIGN in obj:
            split = obj.split(SCOPE_SIGN)
            return split[0], int(split[1])
        else:
            return obj, -1

    def _test_series_of_values(self, obj: Union[str, ObjectId], *expected: Any):
        obj, line_no = self._separate_line_no(obj)
        return self._test_series(obj, lambda value: value, line_no, *expected)

    @classmethod
    @abstractmethod
    def program_path(cls) -> Path:
        raise NotImplementedError()

    @classmethod
    def example(cls, example_test_name: str) -> Path:
        return cls.EXAMPLES_PATH.joinpath(example_test_name, Path(example_test_name).with_suffix('.py'))


class TestNestedObjectBuild(TestDiffObjectBuilder):
    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic2')

    def test_object_name(self):
        self._test_series_of_values('r0',
                                    None,
                                    {'lb': {'_x': 1, '_y': 2}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': -1, '_y': -2}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 0, '_y': 1}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 1, '_y': 2}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 2, '_y': 3}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                                    {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 4, '_y': 4}},
                                    )

    def test_field_access(self):
        self._test_series('r0',
                          lambda value: eval('r0.rt', {'r0': value}),
                          -1,
                          SKIP_VALUE,
                          SKIP_VALUE,
                          {'_x': 3, '_y': 4},
                          {'_x': -1, '_y': -2},
                          {'_x': 0, '_y': 1},
                          {'_x': 1, '_y': 2},
                          {'_x': 2, '_y': 3},
                          {'_x': 3, '_y': 4},
                          {'_x': 4, '_y': 4})


class TestBuiltinCollections(TestDiffObjectBuilder):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic3')

    def test_lists(self):
        self._test_series_of_values('l1', None, [1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6], [1, 2, 4, 5, 6], [6, 5, 4, 2, 1],
                                    [], [6, 7, 8, 9, 10])

    def test_sets(self):
        self._test_series_of_values('s1', None, {1, 2, 3}, {1, 2, 3, 4}, {2, 3, 4}, {2, 3, 4, 5}, {2, 3, 4}, {2, 4},
                                    {1, 2, 3, 4, 5}, {3, 4, 5}, {3, 4, 6, 7}, set())

    def test_tuples(self):
        self._test_series_of_values('t1', None, (1, 2, 3,))

    def test_dicts(self):
        self._test_series_of_values('d1', None, {1: 'a', 2: 'b', 3: 'c'})
        self._test_series_of_values('d2', SKIP_VALUE,
                                    {DiffObjectBuilder.AttributedDict([('value', 'A')]): 1,
                                     DiffObjectBuilder.AttributedDict([('value', 'B')]): 2})
        self._test_series_of_values('d3', SKIP_VALUE,
                                    {DiffObjectBuilder.AttributedDict([('A', 1), ('B', 2)]): 3})


class TestGraph(TestDiffObjectBuilder):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('graphs')

    def test_g(self):
        vertex = lambda val: DiffObjectBuilder.AttributedDict({'value': val})
        edge = lambda f, t, w: DiffObjectBuilder.AttributedDict({'v_from': vertex(f), 'v_to': vertex(t), 'weight': w})
        graph = lambda v, e: DiffObjectBuilder.AttributedDict({'vertices': v, 'edges': e})

        self._test_series_of_values('g',
                                    SKIP_VALUE,
                                    SKIP_VALUE,
                                    graph(set(), set()),
                                    graph({vertex('A')}, set()),
                                    SKIP_VALUE,
                                    graph({vertex('A'), vertex('B')}, {edge('A', 'B', 1)}),
                                    SKIP_VALUE,
                                    graph({vertex('A'), vertex('B'), vertex('C')},
                                          {edge('A', 'B', 1), edge('B', 'C', 2)}),
                                    SKIP_VALUE,
                                    graph({vertex('A'), vertex('B'), vertex('C'), vertex('D')},
                                          {edge('A', 'B', 1), edge('B', 'C', 2), edge('C', 'D', 3)})
                                    )


class TestBasic4(TestDiffObjectBuilder):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic4')

    def test_same_name_multiple_line_no(self):
        self._test_series_of_values('i@2', SKIP_VALUE, *range(5), None)
        self._test_series_of_values('i@7', SKIP_VALUE, *range(5, 11), None)


class TestCaterpillar(TestDiffObjectBuilder):
    @classmethod
    def program_path(cls) -> Path:
        return cls.example('caterpillar')

    def test_same_names_multiple_line_no(self):
        self._test_series_of_values('i@13', None, *range(0, 5), None)
        self._test_series_of_values('total_slices@12', None, *range(0, 12), None)


if __name__ == '__main__':
    unittest.main()
