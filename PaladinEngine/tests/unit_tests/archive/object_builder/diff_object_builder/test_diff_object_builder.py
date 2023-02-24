import unittest
from io import StringIO
from pathlib import Path
from typing import *

from hamcrest import assert_that, is_, all_of

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import ObjectId
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from engine.engine import PaLaDiNEngine


class TestNestedObjectBuild(unittest.TestCase):
    PROGRAM_PATH = Path.cwd().parents[3].joinpath(Path('test_resources'),
                                                  Path('examples'),
                                                  Path('basic2'),
                                                  Path('basic2.py'))

    @classmethod
    def _run_program(cls) -> Archive:
        with open(TestNestedObjectBuild.PROGRAM_PATH) as f:
            original_code = f.read()

            result, archive, thrown_exception = PaLaDiNEngine.execute_with_paladin(original_code,
                                                                                   PaLaDiNEngine.transform(
                                                                                       original_code),
                                                                                   str(cls.PROGRAM_PATH),
                                                                                   -1,
                                                                                   StringIO())

            return archive

    @classmethod
    def setUpClass(cls) -> None:
        cls.archive = cls._run_program()

    def setUp(self) -> None:
        self.diff_object_builder = DiffObjectBuilder(self.archive)

    def _test_serie(self, item: Union[str, ObjectId], *expected_values: Any):
        time_generator = self.diff_object_builder._search_iterator(item)

        first_time, first_value = next(time_generator)

        all_of([assert_that(self.diff_object_builder.build(item, t), is_(None)) for t in range(0, first_time)])

        self.assertDictEqual(self.diff_object_builder.build(item, first_time), expected_values[0])

        last_value = first_value
        expected_index = 0
        for time, value in time_generator:
            if value != last_value and expected_index + 1 < len(expected_values):
                expected_index += 1

            self.assertDictEqual(self.diff_object_builder.build(item, time), expected_values[expected_index])
            last_value = value

    def test_object_name(self):
        self._test_serie('r0',
                         {'lb': {'_x': 1, '_y': 2}},
                         {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                         {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': -1, '_y': -2}},
                         {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 0, '_y': 1}},
                         {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 1, '_y': 2}},
                         {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 2, '_y': 3}},
                         {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                         )

        if __name__ == '__main__':
            unittest.main()
