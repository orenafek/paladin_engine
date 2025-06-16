import os
from typing import Optional, Dict, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Inv(BiLateralOperator, TimeOperator):

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        first = self.first.eval(builder, query_locals, user_aux)
        if len(keys := list(first.all_keys())) > 1:
            raise RuntimeError('Invariant subject must be single keyed')

        key = keys[0]
        first_entries = list(first.satisfies_iterator())
        if len(first_entries) < 2:
            return EvalResult.empty(self.times)

        first_values = {n.time: (o, n) for o, n in zip(first_entries, first_entries[1::])}

        results = []

        def process_time_point(t, first_values, query_locals, key, builder, user_aux, second):
            if t not in first_values:
                return TimeOperator.create_time_eval_result_entry(t, True)
            else:
                o, n = first_values[t]
                inv_locals = {**query_locals, **self._make_inv_local('n', n, key, t),
                              **self._make_inv_local('o', o, key, t)}
                second.update_times([n.time])
                second_res = second.eval(builder, inv_locals, user_aux)[n.time]
                return TimeOperator.create_time_eval_result_entry(n.time, second_res.values[0])

        with ThreadPoolExecutor(os.cpu_count()) as executor:
            futures = {executor.submit(process_time_point, t, first_values, query_locals, key, builder, user_aux,
                                       self.second): t for t in self.times}
            for future in as_completed(futures):
                results.append(future.result())

        return EvalResult(sorted(results, key=lambda e: e.time))


    # def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
    #          user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
    #     first = self.first.eval(builder, query_locals, user_aux)
    #     if len(keys := list(first.all_keys())) > 1:
    #         raise RuntimeError('Invariant subject must be single keyed')
    #
    #     key = keys[0]
    #     first_entries = list(first.satisfies_iterator())
    #     if len(first_entries) < 2:
    #         return EvalResult.empty(self.times)
    #
    #     first_values = {n.time: (o, n) for o, n in zip(first_entries, first_entries[1::])}
    #
    #     results = []
    #     for t in self.times:
    #         if t not in first_values:
    #             results.append(TimeOperator.create_time_eval_result_entry(t, True))
    #         else:
    #             o, n = first_values[t]
    #             inv_locals = {**query_locals, **self._make_inv_local('n', n, key, t),
    #                           **self._make_inv_local('o', o, key, t)}
    #             self.second.update_times([n.time])
    #             results.append(self.second.eval(builder, inv_locals, user_aux)[n.time])
    #
    #     return EvalResult(sorted(results, key=lambda e: e.time))

    def _make_inv_local(self, name, obj, key, time):
        return {name: EvalResult([EvalResultEntry(time, [EvalResultPair(name, obj[key].value)])])}
