import csv
import os
from abc import ABC
from contextlib import redirect_stdout
from pathlib import Path
from subprocess import Popen
from time import time
from typing import List, Optional

from engine.engine import PaLaDiNEngine
from tests.test_common.test_common import TestCommon


class Benchmarker(ABC):
    TIME_FACTOR = 10 ** 4

    def __init__(self, results_path: Path, should_output: bool = True):
        self.results_path = results_path
        self.should_output = should_output
        self._fo = open(self.results_path, 'w+')
        self.writer = csv.writer(self._fo)
        self.engine: Optional[PaLaDiNEngine] = None
        self.pdbrc_path: Optional[Path] = None

    def benchmark(self, progs: List[str | Path]):
        self.writer.writerow(['test_name', *[f.__name__ for f in [self.clean, self.pdb, self.pdb_cond, self.paladin]]])
        for prog in progs:
            self.engine = PaLaDiNEngine(prog, record=False)
            self._measure(self.clean, self.pdb, self.pdb_cond, self.paladin)

        self._fo.close()

    def pdb(self):
        return self._pdb('catch Exception', 'continue', 'quit', pdbrc=True)

    def pdb_cond(self):
        return self._pdb('catch Exception', "break 1, False", 'continue', 'quit', pdbrc=True)

    def _measure(self, *cb):
        try:
            self.writer.writerow([self.engine.source_path.name, *[str(c() * Benchmarker.TIME_FACTOR) for c in cb]])
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


def main():
    b = Benchmarker(Path.cwd().joinpath('benchmark.csv'), should_output=True)
    b.benchmark(TestCommon.all_examples())


if __name__ == '__main__':
    main()
