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

    def _test_series_of_values(self, query: str, *expected):
        self._test_series(query, lambda e: getattr(e, self.__remove_symbols_from_key(query)), -1, *expected)

    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        results = self.paladin_native_parser.parse(obj, self._times().start, self._times().stop, jsonify=False)
        for e in results:
            yield e.time, e

    @staticmethod
    def __remove_symbols_from_key(key: str):
        return re.sub(r'(\$)', '', re.sub(r'(@\d+)', '', key))


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


if __name__ == '__main__':
    unittest.main(module='TestPaladinNativeParser')
