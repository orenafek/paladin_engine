from abc import ABC
from functools import reduce
from typing import Iterable, Optional, Dict, Collection, List, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Replacement, \
    EvalResultEntry, EvalResultPair, Time
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator, BiLateralOperator, \
    VariadicLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class TimeOperator(Operator, ABC):
    TIME_KEY = '__TIME'

    @classmethod
    def make(cls, op: Operator):
        return op if isinstance(op, TimeOperator) else Whenever(op.times, op)

    def __init__(self, times: Iterable[Time]):
        super().__init__(times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        raise NotImplementedError()

    def _get_args(self) -> Collection['Operator']:
        return [self.op]

    @staticmethod
    def create_time_eval_result_entry(t: Time, res: bool,
                                      rep: Optional[List[Replacement]] = None) -> EvalResultEntry:
        return EvalResultEntry(t, [EvalResultPair(TimeOperator.TIME_KEY, res)], rep if rep is not None else [])


class BiTimeOperator(BiLateralOperator, TimeOperator, ABC):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator,
                 bi_result_maker: Callable[[bool, bool], bool]):
        BiLateralOperator.__init__(self, times, first, second)
        TimeOperator.__init__(self, times)
        self.bi_result_maker = bi_result_maker

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = TimeOperator.make(self.first).eval(builder, query_locals)
        second = TimeOperator.make(self.second).eval(builder, query_locals)

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(e1.time, self._make_res(e1, e2),
                                                       e1.replacements + e2.replacements)

            for e1, e2 in zip(first, second)])

    def _make_res(self, e1: EvalResultEntry, e2: EvalResultEntry) -> bool:
        return self.bi_result_maker(e1[TimeOperator.TIME_KEY].value, e2[TimeOperator.TIME_KEY].value)


class Whenever(VariadicLateralOperator, TimeOperator):

    def __init__(self, times: Iterable[Time], *args: Operator):
        VariadicLateralOperator.__init__(self, times, *args)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        evaled_args = list(map(lambda arg: arg.eval(builder, query_locals), self.args))
        arg_results = list(map(lambda er: lambda t: er[t].satisfies(), evaled_args))

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, all([arg_res(t) for arg_res in arg_results]),
                                                       list(reduce(lambda l, rep: l + rep,
                                                                   map(lambda ar: ar[t].replacements, evaled_args),
                                                                   [])))
            for t in self.times
        ])
