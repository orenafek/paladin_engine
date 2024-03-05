import csv
import os
from abc import ABC
from contextlib import redirect_stdout
from pathlib import Path
from subprocess import Popen
from time import time
from typing import List, Optional, Tuple, Callable

from engine.engine import PaLaDiNEngine
from tests.test_common.test_common import TestCommon


class Benchmarker(ABC):
    TIME_FACTOR = 10 ** 4

    def __init__(self, results_path: Path, should_output: bool = True):
        self.header = []
        self.rows = []
        self.results_path = results_path
        self.should_output = should_output
        self._fo = open(self.results_path, 'w+')
        self.writer = csv.writer(self._fo)
        self.engine: Optional[PaLaDiNEngine] = None
        self.pdbrc_path: Optional[Path] = None

    def benchmark(self, progs: List[str | Path]):
        self.header = ['test_name',
                       *[f.__name__ for f in [self.clean, self.pdb, self.pdb_cond, self.paladin]] + [
                           f'{self.paladin.__name__}/{self.pdb_cond.__name__}']]
        self.writer.writerow(self.header)

        for prog in progs:
            self.engine = PaLaDiNEngine(prog, record=False)
            self._measure(self.clean, self.pdb, self.pdb_cond, self.paladin)

        self._post_process((self.paladin, self.pdb_cond))
        self._finalize()
        self._fo.close()

    def pdb(self):
        return self._pdb('catch Exception', 'continue', 'quit', pdbrc=True)

    def pdb_cond(self):
        return self._pdb('catch Exception', "break 1, False", 'continue', 'quit', pdbrc=True)

    def _measure(self, *cb):
        try:
            self.rows.append([self.engine.source_path.name, *[str(c() * Benchmarker.TIME_FACTOR) for c in cb]])
        except:
            return

    def clean(self):
        start_time = time()
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
        popen = Popen(f'python -m pdb {str(self.engine.source_path)}', shell=True,
                      stdout=None if self.should_output else os.devnull)
        popen.wait()
        end_time = time()
        if self.pdbrc_path.exists():
            self.pdbrc_path.unlink()

        return end_time - start_time

    def paladin(self):
        start_time = time()
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
