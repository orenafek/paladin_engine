import unittest
from io import StringIO
from pathlib import Path
from typing import *

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import ObjectId
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from engine.engine import PaLaDiNEngine


class TestNestedObjectBuild(unittest.TestCase):
    PROGRAM_PATH = Path(__file__).parents[4].joinpath(Path('test_resources'),
                                                  Path('examples'),
                                                  Path('basic2'),
                                                  Path('basic2.py'))
    SKIP_VALUE = 'SKIP!'

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

    def _test_series(self, obj: Union[str, ObjectId], actual_value_generator: Callable[Any, Any], *expected: Any):
        last_value = None
        expected_index = 0
        for time, value in self.diff_object_builder._build_iterator(obj):
            if value != last_value and expected_index + 1 < len(expected):
                expected_index += 1
            last_value = value

            if expected[expected_index] == TestNestedObjectBuild.SKIP_VALUE:
                continue

            self.assertEqual(expected[expected_index], actual_value_generator(value))

    def test_object_name(self):
        self._test_series('r0',
                          lambda value: value,
                          None,
                          {'lb': {'_x': 1, '_y': 2}},
                          {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                          {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': -1, '_y': -2}},
                          {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 0, '_y': 1}},
                          {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 1, '_y': 2}},
                          {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 2, '_y': 3}},
                          {'lb': {'_x': 1, '_y': 2}, 'rt': {'_x': 3, '_y': 4}},
                          )

    def test_field_access(self):
        self._test_series('r0',
                          lambda value: eval('r0.rt', {'r0': value}),
                          TestNestedObjectBuild.SKIP_VALUE,
                          TestNestedObjectBuild.SKIP_VALUE,
                          {'_x': 3, '_y': 4},
                          {'_x': -1, '_y': -2},
                          {'_x': 0, '_y': 1},
                          {'_x': 1, '_y': 2},
                          {'_x': 2, '_y': 3},
                          {'_x': 3, '_y': 4})

if __name__ == '__main__':
    unittest.main()
