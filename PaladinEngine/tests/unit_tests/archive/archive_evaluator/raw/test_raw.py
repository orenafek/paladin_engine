import unittest
from abc import ABC
from pathlib import Path
from typing import Union, Any, Optional, Iterator, Tuple

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import ObjectId, Time, Identifier
from archive.archive_evaluator.paladin_dsl_semantics import Raw, Operator
from archive.archive_evaluator.paladin_native_parser import PaladinNativeParser
from tests.test_common.test_common import SKIP_VALUE
from tests.unit_tests.archive.object_builder.diff_object_builder.test_diff_object_builder import TestDiffObjectBuilder, \
    TestCaterpillar
from utils.utils import separate_line_no


class TestRaw(TestDiffObjectBuilder, ABC):

    def _test_series_of_values_no_scope_split(self, obj: Identifier, *expected: Any):
        return self._test_series(Raw(obj, -1, self._times()), lambda v: v, -1, *expected)

    def _test_series_of_values(self, obj: Identifier, *expected: Any):
        obj, line_no = separate_line_no(obj)
        raw_op = Raw(obj, line_no, self._times())
        return self._test_series(raw_op, lambda v: v, line_no, *expected)

    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        assert isinstance(obj, Operator)
        for e in obj.eval(self.diff_object_builder):
            yield e.time, getattr(e, obj.query)


# noinspection DuplicatedCode
class TestBasic4Raw(TestRaw):
    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic4')

    def test_same_name_multiple_line_no(self):
        self._test_series_of_values('i@2', SKIP_VALUE, *range(5), None)
        self._test_series_of_values('i@7', SKIP_VALUE, *range(5, 11), None)

    def test_function_call_ret_value(self):
        self._test_series_of_values(f'square',
                                    SKIP_VALUE,
                                    *[x * x for x in range(1, 11)],
                                    None)


class TestCaterpillarRaw(TestRaw, TestCaterpillar):
    program_path = TestCaterpillar.program_path


if __name__ == '__main__':
    unittest.main()
