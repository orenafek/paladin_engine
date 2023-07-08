import re
import unittest
from abc import ABC
from pathlib import Path
from typing import Tuple, Any, Iterator, Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time
from archive.archive_evaluator.paladin_native_parser import PaladinNativeParser
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from tests.test_common.test_common import TestCommon, SKIP_VALUE
from tests.unit_tests.archive.object_builder.diff_object_builder.test_diff_object_builder import TestBasic4


class TestPaladinNativeParser(TestCommon, ABC):

    def setUp(self) -> None:
        self.paladin_native_parser = PaladinNativeParser(self.archive)
        self.read_aux_file()

    def _test_series_of_values(self, query: str, *expected):
        self._test_series(query, lambda e: getattr(e, self.remove_symbols_from_key(query)), -1, *expected)

    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        if self.aux_file_content is not None:
            self.paladin_native_parser.add_user_aux(self.aux_file_content)

        results = self.paladin_native_parser.parse(obj, self._times().start, self._times().stop, jsonify=False)
        for e in results:
            yield e.time, e

        self.paladin_native_parser.remove_user_aux()

    @staticmethod
    def remove_symbols_from_key(key: str):
        return re.sub(r'(\$)', '', re.sub(r'(@\d+)', '', key))

    @classmethod
    def make_example_aux(cls):
        return cls.program_path().parent.joinpath(Path(cls.example_aux_file_name()))

    @classmethod
    def example_aux_file_name(cls) -> Optional[str]:
        return None

    def read_aux_file(self):
        if self.__class__.example_aux_file_name():
            with self.__class__.make_example_aux().open('r') as f:
                self.aux_file_content = f.read()
        else:
            self.aux_file_content = None


class TestCaterpillarParser(TestPaladinNativeParser):

    @classmethod
    def program_path(cls):
        return cls.example('caterpillar')

    def test_left_join(self):
        query = \
            '[(e1.total_slices, ' \
            '{e2.total_slices for e2 in ''Where(Union(total_slices@12, i@13, j@14), LineHit(16))' \
            ' if e1.i == e2.i and e1.j and (e1.j + 1 == e2.j)}) ' \
            'for e1 in Where(Union(total_slices@26, i@25, j@25), LineHit(30))]'
        self._test_series_of_values(
            query,
            SKIP_VALUE,
            (None, set()),
            (1, set()),
            (None, set()),
            *[j for t in zip([(i, {i}) for i in range(2, 12)], [(None, set())] * 10) for j in t])


class TestBasic4Parser(TestPaladinNativeParser):
    program_path = TestBasic4.program_path

    def test_function_call_ret_value(self):
        self._test_series_of_values(f'$square',
                                    SKIP_VALUE,
                                    SKIP_VALUE,
                                    *[x * x for x in range(1, 11)],
                                    None)


class TestKruskalLetAndAux(TestPaladinNativeParser):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('kruskal')

    @classmethod
    def example_aux_file_name(cls) -> Optional[str]:
        return 'kruskal_aux.py'

    def test_find_with_aux(self):
        query = "Let({'x': {0, 1, 2}}, Where(list(map(lambda i: uf_find(uf@53, i), [0, 1, 2])), " \
                "And(src@56 in x, dest@57 in x)))"

        self.remove_symbols_from_key = lambda _: 'list(map(lambda i: uf_find(uf, i), [0, 1, 2]))'
        self._test_series_of_values(query,
                                    SKIP_VALUE,
                                    SKIP_VALUE,
                                    [0, 1, 2],
                                    [0, 1, 0],
                                    SKIP_VALUE,
                                    [0, 0, 0],
                                    SKIP_VALUE,
                                    [0, 0, 0],
                                    SKIP_VALUE)


if __name__ == '__main__':
    unittest.main(module='TestPaladinNativeParser')
