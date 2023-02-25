import csv
import unittest
from abc import abstractmethod, ABC
from io import StringIO
from pathlib import Path
from typing import *

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import ObjectId
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from engine.engine import PaLaDiNEngine


class TestDiffObjectBuilder(unittest.TestCase, ABC):
    SKIP_VALUE = 'SKIP!'
    TEST_RESOURCES_PATH = Path(__file__).parents[4].joinpath('test_resources')
    EXAMPLES_PATH = TEST_RESOURCES_PATH.joinpath('examples')

    @classmethod
    def _run_program(cls) -> Archive:
        with open(cls.program_path()) as f:
            original_code = f.read()
            paladinized_code = PaLaDiNEngine.transform(original_code)
            TestDiffObjectBuilder.__write_paladinized_code(cls.program_path(), paladinized_code)
            result, archive, thrown_exception = PaLaDiNEngine.execute_with_paladin(original_code,
                                                                                   paladinized_code,
                                                                                   str(cls.program_path()),
                                                                                   -1,
                                                                                   StringIO())

            TestDiffObjectBuilder.__dump_to_csv(archive, cls.program_path())
            return archive

    @staticmethod
    def __write_paladinized_code(original_program_path: Path, paladinized_code: str):
        with open(str(original_program_path.with_suffix('')) + "_output.py", 'w+') as fo:
            fo.write(PaLaDiNEngine.import_line('stubs.stubs'))
            fo.writelines('\n' * 3)
            fo.write(paladinized_code)

    @staticmethod
    def __dump_to_csv(archive: Archive, original_program_path: Path) -> None:
        with open(str(original_program_path.with_suffix('.csv')), 'w+') as fo:
            writer = csv.writer(fo)
            header, rows = archive.to_table()
            writer.writerow(header)
            writer.writerows(rows)

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

        self.assertEqual(len(expected) - 1, expected_index)

    def _test_series_of_values(self, obj: Union[str, ObjectId], *expected: Any):
        return self._test_series(obj, lambda value: value, *expected)

    @classmethod
    @abstractmethod
    def program_path(cls) -> Path:
        raise NotImplementedError()


class TestNestedObjectBuild(TestDiffObjectBuilder):
    @classmethod
    def program_path(cls) -> Path:
        return cls.EXAMPLES_PATH.joinpath('basic2', 'basic2.py')

    def test_object_name(self):
        self._test_series_of_values('r0',
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


class TestBuiltinCollections(TestDiffObjectBuilder):

    @classmethod
    def program_path(cls) -> Path:
        return cls.EXAMPLES_PATH.joinpath('basic3', 'basic3.py')

    def test_lists(self):
        self._test_series_of_values('l1', None, [1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6], [1, 2, 4, 5, 6], [6, 5, 4, 2, 1],
                                    [], [6, 7, 8, 9, 10])

    def test_sets(self):
        self._test_series_of_values('s1', None, {1, 2, 3}, {1, 2, 3, 4}, {2, 3, 4}, {2, 3, 4, 5}, {2, 3, 4}, {2, 4},
                                    {1,2,3,4,5}, {3,4,5}, {3,4,6,7}, set())

    def test_tuples(self):
        self._test_series_of_values('t1', None, (1, 2, 3,))

    def test_dicts(self):
        self._test_series_of_values('d1', None, {1: 'a', 2: 'b', 3: 'c'})


if __name__ == '__main__':
    unittest.main()
