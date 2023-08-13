from dataclasses import dataclass
from typing import Optional, Any, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import OperatorResults, UserAux
from archive.object_builder.object_builder import ObjectBuilder


@dataclass
class OperatorEvalData(object):
    builder: ObjectBuilder
    query_locals: Optional[OperatorResults] = None
    user_aux: Optional[UserAux] = None
    bounded: Optional[Dict[str, Any]] = None
