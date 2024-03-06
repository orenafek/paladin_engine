import csv
import os
from abc import ABC
from contextlib import redirect_stdout
from functools import wraps
from pathlib import Path
from subprocess import Popen
from time import time
from typing import List, Optional, Tuple, Callable, Iterable

from archive.archive_evaluator.paladin_native_parser import PaladinNativeParser
from engine.engine import PaLaDiNEngine
from tests.test_common.test_common import TestCommon

TIME_FACTOR = 10 ** 4
REPEAT_COUNT = 5


def TimedTest(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return TIME_FACTOR * (f(*args, **kwargs) / REPEAT_COUNT)

    return wrapper


class Benchmarker(ABC):
    def __init__(self, results_path: Path, should_output: bool = True):
        self.header = []
        self.rows = []
        self.results_path = results_path
        self.should_output = should_output
        self._fo = open(self.results_path, 'w+')
        self.writer = csv.writer(self._fo)
        self.engine: Optional[PaLaDiNEngine] = None
        self.pdbrc_path: Optional[Path] = None

    @property
    def benchmark_tests(self) -> Iterable[Callable]:
        return [self.source_line_count, self.instrument, self.clean, self.pdb, self.pdb_cond, self.paladin,
                self.log_construction]

    def benchmark(self, progs: List[str | Path]):
        self.header = ['test_name',
                       *[f.__name__ for f in self.benchmark_tests] + [
                           f'{self.paladin.__name__}/{self.pdb_cond.__name__}']]
        self.writer.writerow(self.header)

        for prog in progs:
            print(f'Running {prog.name}')
            self.engine = PaLaDiNEngine(prog, record=False)
            self._measure(*self.benchmark_tests)

        self._post_process((self.paladin, self.pdb_cond))
        self._finalize()
        self._fo.close()

    def source_line_count(self):
        return len([r for r in self.engine.source_code.split(os.linesep) if r != ''])

    @TimedTest
    def pdb(self):
        return self._pdb('continue', 'quit', pdbrc=True)

    @TimedTest
    def pdb_cond(self):
        return self._pdb("break 1, False", 'continue', 'quit', pdbrc=True)

    def _measure(self, *cb):
        try:
            self.rows.append([self.engine.source_path.name, *[str(c()) for c in cb]])
        except Exception as e:
            return

    def instrument(self):
        return self.engine.transformation_time

    @TimedTest
    def log_construction(self):
        parser = PaladinNativeParser(self.engine.run_data.archive, True)
        return parser.construction_time

    @TimedTest
    def clean(self):
        start_time = time()
        for _ in range(REPEAT_COUNT):
            if self.should_output:
                exec(self.engine.source_code, {}, {})
            else:
                with redirect_stdout(open(os.devnull, 'w')):
                    exec(self.engine.source_code, {}, {})
        end_time = time()
        return end_time - start_time

    def _pdb(self, *commands: str, pdbrc: bool = False):
        if pdbrc:
            self.pdbrc_path = Path.cwd().joinpath('.pdbrc')
            if self.pdbrc_path.exists():
                self.pdbrc_path.unlink()
            with open(self.pdbrc_path, 'w+') as f:
                f.write('\n'.join(commands))

        start_time = time()
        for _ in range(REPEAT_COUNT):
            popen = Popen(f'python {str(self.engine.source_path)}', shell=True,
                          stdout=None if self.should_output else os.devnull)
            popen.wait()
        end_time = time()
        if self.pdbrc_path.exists():
            self.pdbrc_path.unlink()

        return end_time - start_time

    @TimedTest
    def paladin(self):
        start_time = time()
        for _ in range(REPEAT_COUNT):
            self.engine.execute_with_paladin()
        end_time = time()
        return end_time - start_time

    def _post_process(self, *calc_func_pairs: Tuple[Callable, Callable]):
        for calc_over, calc_under in calc_func_pairs:
            calc_over_col_index = self.header.index(calc_over.__name__)
            calc_under_col_index = self.header.index(calc_under.__name__)

            for r in self.rows:
                r.append(str(float(r[calc_over_col_index]) / float(r[calc_under_col_index])))

    def _finalize(self):
        self.writer.writerows(self.rows)


def main():
    b = Benchmarker(output_path := Path.cwd().joinpath('benchmark.csv'), should_output=True)
    print(output_path)
    b.benchmark(TestCommon.all_examples())


if __name__ == '__main__':
    main()
