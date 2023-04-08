import unittest
from abc import ABC
from pathlib import Path
from typing import Any

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Identifier
from archive.archive_evaluator.paladin_dsl_semantics import Raw
from archive.archive_evaluator.paladin_dsl_semantics.changed import Changed
from tests.unit_tests.archive.archive_evaluator.time_operator.test_time_operator import TestTimeOperator
from tests.unit_tests.archive.object_builder.diff_object_builder.test_diff_object_builder import TestDiffObjectBuilder


class TestChanged(TestDiffObjectBuilder, TestTimeOperator, ABC):
    def _test_times(self, obj: Identifier, *expected: Any):
        obj_no_line_no, line_no = self._separate_line_no(obj)
        TestTimeOperator._test_times(self,
                                     Changed(self.times(), Raw(obj_no_line_no, line_no, self.times()))
                                     .eval(self.diff_object_builder), *expected)


class TestBasic5Changed(TestChanged):
    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic5')

    def test_changed_primitives(self):
        self._test_times('x', [1, 8, 21])
        self._test_times('y', [2, 9, 22])
        self._test_times('z', [4, 5])


if __name__ == '__main__':
    unittest.main()
