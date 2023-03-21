import unittest
from abc import ABC
from typing import Union, Any, Iterable, Optional, Iterator, Tuple

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import ObjectId, Time, LineNo
from archive.archive_evaluator.paladin_dsl_semantics import Raw, Operator
from tests.unit_tests.archive.object_builder.diff_object_builder.test_diff_object_builder import TestDiffObjectBuilder, \
    TestBasic4, TestCaterpillar


class TestRaw(TestDiffObjectBuilder, ABC):

    def _test_series_of_values_no_scope_split(self, obj: Union[str, ObjectId], *expected: Any):
        return self._test_series(Raw(obj, -1, self._times()), lambda v: v, -1, *expected)

    def _test_series_of_values(self, obj: Union[str, ObjectId], *expected: Any):
        obj, line_no = self._separate_line_no(obj)
        raw_op = Raw(obj, line_no, self._times())
        return self._test_series(raw_op, lambda v: v, line_no, *expected)

    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        assert isinstance(obj, Operator)
        for e in obj.eval(self.diff_object_builder):
            yield e.time, getattr(e, obj.query)


class TestBasic4Raw(TestRaw, TestBasic4):
    pass


class TestCaterpillarRaw(TestRaw, TestCaterpillar):
    pass


if __name__ == '__main__':
    unittest.main()
