from pathlib import Path

from tests.test_common.test_common import SKIP_VALUE
from tests.test_common.test_object_builder.test_object_builder import TestObjectBuilder


class TestJobsDemo(TestObjectBuilder):

    @classmethod
    def program_path(cls) -> Path:
        return cls.example('jobs_demo')

    def test_scenario(self):
        self._test_series_of_values('server', SKIP_VALUE, {'summaries': [], 'todo': []})
