import unittest
from abc import ABC
from pathlib import Path
from typing import Any

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Identifier
from archive.archive_evaluator.paladin_dsl_semantics import Raw
from archive.archive_evaluator.paladin_dsl_semantics.changed import Changed
from tests.unit_tests.archive.archive_evaluator.time_operator.test_time_operator import TestTimeOperator
from tests.unit_tests.archive.object_builder.test_object_builder import TestObjectBuilder
from utils.utils import separate_line_no


class TestChanged(TestObjectBuilder, TestTimeOperator, ABC):
    def _test_times(self, obj: Identifier, *expected: Any):
        obj_no_line_no, line_no = separate_line_no(obj)
        TestTimeOperator._test_times(self,
                                     Changed(self.times(), Raw(obj_no_line_no, line_no, self.times()))
                                     .eval(self.object_builder), *expected)


class TestBasic5Changed(TestChanged):
    @classmethod
    def program_path(cls) -> Path:
        return cls.example('basic5')

    def test_changed_primitives(self):
        self._test_times('x', [2, 10, 21])
        self._test_times('y', [3, 11, 22])
        self._test_times('z', [6, 7])


if __name__ == '__main__':
    unittest.main()
