from abc import ABC, abstractmethod
from typing import *

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import LineNo, Time, ObjectId, Identifier


class ObjectBuilder(ABC):
    def __init__(self, archive: Archive):
        self.archive: Archive = archive

    @abstractmethod
    def build(self, item: Identifier, t: Time, line_no: Optional[LineNo] = -1) -> Any:
        raise NotImplementedError()

    def find_events(self, line_no):
        return self.archive.find_events(line_no)

    def get_loop_iterations(self, line_no: LineNo):
        return self.archive.get_loop_iterations(line_no)

    def get_assignments(self, time_range: range, line_no_range: range):
        return self.archive.get_assignments(time_range, line_no_range)

    @abstractmethod
    def get_change_times(self, name: str, line_no: LineNo = -1):
        raise NotImplementedError()
