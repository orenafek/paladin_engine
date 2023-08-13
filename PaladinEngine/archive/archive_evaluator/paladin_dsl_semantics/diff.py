from typing import Any

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair, Time
from archive.archive_evaluator.operator_eval_results import OperatorEvalData
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator


class Diff(BiLateralOperator):
    """
          Diff(e1, e2): Calculates the difference between two entries.
    """

    def eval(self, eval_data: OperatorEvalData):
        first = self.first.eval(eval_data)
        second = self.second.eval(eval_data)

        return EvalResult(
            [EvalResultEntry(t,
                             [EvalResultPair(k, Diff._entries_diff(t, e1, e2)) for k in first.all_keys()])
             for e1, e2 in zip(first, second) for t in self.times]
        )

    @staticmethod
    def _entries_diff(t: Time, e1: EvalResultEntry, e2: EvalResultEntry) -> EvalResultEntry:
        return EvalResultEntry(t, [
            EvalResultPair(k1, Diff._calculate_diff(e1[k1].value, e2[k2].value)) for k1, k2 in zip(e1.keys, e2.keys)
        ])

    @staticmethod
    def _calculate_diff(v1: Any, v2: Any) -> Any:
        if type(v1) != type(v2):
            return None

        match v1:
            case list():
                return [i for i in v1 if i not in v2]

            case set():
                return v1 - v2

            case dict():
                shared_keys = v1.keys().intersection(v2.keys())
                only_v1_keys = v1.keys() - v2.keys()
                return {**{k: v2[k] for k in shared_keys}, **{k: v for k, v in v1.items() if k in only_v1_keys}}

        return None
