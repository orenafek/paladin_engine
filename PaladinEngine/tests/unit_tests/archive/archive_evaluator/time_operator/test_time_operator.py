from abc import ABC
from typing import Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator
from tests.test_common.test_common import TestCommon


class TestTimeOperator(TestCommon, ABC):

    def _test_times(self, r: EvalResult, true_times: Iterable[Time]):
        for e in r:
            self.assertEqual(getattr(e, TimeOperator.TIME_KEY), e.time in true_times)
