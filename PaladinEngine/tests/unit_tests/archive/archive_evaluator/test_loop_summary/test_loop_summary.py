from abc import ABC
from typing import Any

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Identifier
from tests.unit_tests.archive.object_builder.test_object_builder import TestObjectBuilder


class TestLoopSummary(TestObjectBuilder, ABC):
    def _test_series_of_values(self, obj: Identifier, *expected: Any):
        return super()._test_series_of_values(obj, *expected)