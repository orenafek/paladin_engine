from abc import ABC, abstractmethod
from typing import *

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import LineNo, Time, ObjectId, \
    Identifier, ContainerId


class ObjectBuilder(ABC):
    def __init__(self, archive: Archive):
        self.archive: Archive = archive

    @abstractmethod
    def build(self, item: Identifier, t: Time, line_no: Optional[LineNo] = -1) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def get_type(self, item: Identifier, time: Time, line_no: Optional[LineNo] = -1) -> Optional[Type]:
        raise NotImplementedError()

    def find_events(self, line_no):
        return self.archive.find_events(line_no)

    def get_loop_iterations(self, line_no: LineNo):
        return self.archive.get_loop_iterations(line_no)

    def get_loop_starts(self, line_no: LineNo):
        return self.archive.get_loop_starts(line_no)

    def get_assignments(self, time_range: range, line_no_range: range):
        return self.archive.get_assignments(time_range, line_no_range)

    def get_line_nos_for_time(self, line_no: LineNo) -> Iterable[Time]:
        return self.archive.get_line_nos_for_time(line_no)

    @abstractmethod
    def get_change_times(self, name: str, line_no: LineNo = -1):
        raise NotImplementedError()

    @abstractmethod
    def get_line_no_by_name_and_container_id(self, name: str, container_id: ContainerId = -1) -> LineNo:
        raise NotImplementedError()

    def get_function_entries(self, func_name: str, line_no: LineNo, entrances: bool = True, exits: bool = True):
        return self.archive.get_function_entries(func_name, line_no, entrances, exits)
