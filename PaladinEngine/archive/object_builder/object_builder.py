from abc import ABC, abstractmethod
from typing import *

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import LineNo, Time, Identifier, \
    ContainerId


class ObjectBuilder(ABC):
    def __init__(self, archive: Archive, should_time_construction: bool = False):
        self.archive: Archive = archive
        self._should_time_construction: bool = should_time_construction

    @abstractmethod
    def build(self, item: Identifier, t: Time, _type: Type = Any, line_no: Optional[LineNo] = -1) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def get_type(self, item: Identifier, time: Time, line_no: Optional[LineNo] = -1) -> Optional[Type]:
        raise NotImplementedError()

    def find_events(self, line_no: Time = -1, time_range: Iterable[Time] = None):
        return self.archive.find_events(line_no, time_range)

    def get_loop_iterations(self, line_no: LineNo):
        return self.archive.get_loop_iterations(line_no)

    def get_loop_starts(self, line_no: LineNo):
        return self.archive.get_loop_starts(line_no)

    def get_assignments(self, time_range: range, line_no_range: range):
        return self.archive.get_assignments(time_range, line_no_range)

    def get_line_nos_for_time(self, time: Time) -> Iterable[Time]:
        return self.archive.get_line_nos_for_time(time)

    @abstractmethod
    def get_change_times(self, name: str, line_no: LineNo = -1):
        raise NotImplementedError()

    @abstractmethod
    def get_line_no_by_name_and_container_id(self, name: str, container_id: ContainerId = -1) -> LineNo:
        raise NotImplementedError()

    def get_function_entries(self, func_name: str, line_no: LineNo, entrances: bool = True, exits: bool = True,
                             ass_and_bmfcs_only: bool = False):
        return self.archive.get_function_entries(func_name, line_no, entrances=entrances, exits=exits,
                                                 ass_and_bmfcs_only=ass_and_bmfcs_only)

    def get_function_line_nos(self, func_name: str):
        return self.archive.get_function_line_nos(func_name)

    def get_call_chain(self, include_builtins=True) -> Dict[Time, Tuple[str, str]]:
        return self.archive.get_call_chain(include_builtins)

    @property
    def construction_time(self):
        return 0

    def _build_iterator(self, obj: Identifier, line_no: Optional[LineNo] = -1) -> \
            Optional[Iterator[Tuple[Time, Any]]]:
        for t in range(0, self.archive.last_time):
            yield t, self.build(obj, t, type(obj), line_no)

        return None

    @staticmethod
    def _add_attributes(evaluated_object: Dict):
        for f, v in evaluated_object.items():
            if isinstance(f, str):
                setattr(evaluated_object, f, v)