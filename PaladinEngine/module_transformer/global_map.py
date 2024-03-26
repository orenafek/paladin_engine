from dataclasses import dataclass, field
from typing import Dict, Tuple

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import LineNo


@dataclass
class GlobalMap(object):
    functions: Dict[str, Tuple[LineNo, LineNo]] = field(default_factory=lambda: {})
