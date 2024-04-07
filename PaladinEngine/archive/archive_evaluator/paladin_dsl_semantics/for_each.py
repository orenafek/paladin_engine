from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.operator import TriLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.object_builder.object_builder import ObjectBuilder


class ForEach(TriLateralOperator):
    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        if not isinstance(self.second, Raw):
            return EvalResult.empty(self.times)

        var: str = self.second.query

        iter_res: EvalResult = self.third.eval(builder, query_locals, user_aux)
        if iter_res.is_empty():
            return EvalResult.empty(self.times)

        res = []
        for t in self.times:
            # first_res = self.first.eval(builder, ForEach.query_locals_for_compr(query_locals, var, iter_res[t]), user_aux)
            #            query = f'[{self.first.query} for {var} in e]'
            query = f'list(map(lambda {var}: {self.first.query}, e.{self.third.query}))'
            first_res = Raw(query, times=[t]).eval(builder,
                                                   ForEach.query_locals_for_compr(query_locals, 'e', iter_res, t),
                                                   user_aux)
            res.append(EvalResultEntry(t, [EvalResultPair(k, v) for k, v in first_res[t].items]))

        return EvalResult(res)
        # return self.first.eval(builder, {**query_locals, **(ForEach.query_locals_for_compr(var, iter_res))}, user_aux)

    @staticmethod
    def query_locals_for_compr(query_locals, var: str, iter_res: EvalResult, t: Time) -> Dict[str, EvalResult]:
        # return {**query_locals, var: EvalResult([EvalResultEntry(e.time, [EvalResultPair(var, e.items)]) for e in iter_res])}
        return {**query_locals,
                var: EvalResult([EvalResultEntry(t, [EvalResultPair(k, v) for k, v in iter_res[t].items])])}
        # return [AttributedDict(e.items) for e in iter_res]
