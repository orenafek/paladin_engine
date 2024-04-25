from abc import ABC
from typing import Optional, Iterator, Tuple, Any

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, Identifier
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from tests.test_common.test_common import TestCommon
from utils.utils import separate_line_no


class TestObjectBuilder(TestCommon, ABC):
    def setUp(self) -> None:
        self.object_builder = DiffObjectBuilder(self.archive)

    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        return self.object_builder._build_iterator(obj, line_no)

    def _test_series_of_values(self, obj: Identifier, *expected: Any):
        obj, line_no = separate_line_no(obj)
        return self._test_series(obj, lambda value: value, line_no, *expected)
