from abc import ABC, abstractmethod
from typing import *

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import LineNo, Time, ObjectId


class ObjectBuilder(ABC):
    @abstractmethod
    def build(self, item: Union[str, ObjectId], t: Time, line_no: Optional[LineNo] = -1) -> Any:
        raise NotImplementedError()

    def find_events(self, line_no):
        raise NotImplementedError()
