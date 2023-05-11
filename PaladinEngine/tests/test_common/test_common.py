import csv
import unittest
from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Tuple, Iterator, Optional

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, LineNo
from engine.engine import PaLaDiNEngine

SKIP_VALUE = 'SKIP!'


class TestCommon(unittest.TestCase, ABC):
    TEST_RESOURCES_PATH = Path(__file__).parents[1].joinpath('test_resources')
    EXAMPLES_PATH = TEST_RESOURCES_PATH.joinpath('examples')

    @classmethod
    @abstractmethod
    def program_path(cls) -> Path:
        raise NotImplementedError()

    @classmethod
    def example(cls, example_test_name: str) -> Path:
        return cls.EXAMPLES_PATH.joinpath(example_test_name, Path(example_test_name).with_suffix('.py'))

    @classmethod
    def _run_program(cls) -> Archive:
        with open(cls.program_path()) as f:
            original_code = f.read()
            paladinized_code = PaLaDiNEngine.transform(original_code)
            TestCommon.__write_paladinized_code(cls.program_path(), paladinized_code)
            result, archive, thrown_exception = PaLaDiNEngine.execute_with_paladin(original_code,
                                                                                   paladinized_code,
                                                                                   str(cls.program_path()),
                                                                                   -1,
                                                                                   StringIO())

            TestCommon.__dump_to_csv(archive, cls.program_path())
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

    @classmethod
    def tearDownClass(cls) -> None:
        cls.archive.reset()

    @classmethod
    def _times(cls) -> range:
        return range(0, cls.archive.last_time + 1)

    @abstractmethod
    def value_generator(self, obj, line_no) -> Optional[Iterator[Tuple[Time, Any]]]:
        raise NotImplementedError()

    def _test_series(self, obj: Any, actual_value_generator: Callable[[Any], Any], line_no: LineNo, *expected: Any):
        last_value = None
        expected_index = 0
        time = 0
        try:
            for time, value in self.value_generator(obj, line_no):
                if value != last_value and expected_index + 1 < len(expected):
                    expected_index += 1
                last_value = value

                if expected[expected_index] == SKIP_VALUE:
                    continue

                self.assertEqual(expected[expected_index], actual_value_generator(value),
                                 msg=f'time={time}, expected_index={expected_index}')

            self.assertEqual(len(expected) - 1, expected_index)
        except BaseException as e:
            print(f'Exception on time {time}:')
            raise e

    @classmethod
    def times(cls):
        # noinspection PyUnresolvedReferences
        return range(cls.archive.last_time + 1)
