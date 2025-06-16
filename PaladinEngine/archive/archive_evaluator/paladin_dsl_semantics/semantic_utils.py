import re

import more_itertools

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import SemanticsArgType
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import *
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from ast_common.ast_common import *


class SemanticsUtils(object):

    @staticmethod
    def selectors(res: SemanticsArgType) -> List[str]:
        if isinstance(res, bool):
            return []

        first_result_selectors = list(res[list(res.keys())[0]][0].keys())

        assert all(list(res[k][0].keys()) == first_result_selectors for k in res)

        return first_result_selectors

    @staticmethod
    def joined_times(r1: SemanticsArgType, r2: SemanticsArgType) -> Set[int]:
        if isinstance(r1, bool) or isinstance(r2, bool):
            return set()

        return set(r1.keys()).union(r2.keys())

    @staticmethod
    def remove_none_prefix(r: SemanticsArgType) -> SemanticsArgType:
        if isinstance(r, bool):
            return r

        return {k: r[k] for k in list(list(r.keys())[more_itertools.first([_k for _k in r.keys() if
                                                                           any(r[_k][0][s] is not None for s in
                                                                               r[_k][0].keys())])::])}

    @staticmethod
    def _selector_re() -> str:
        return fr"(?P<name>\w+)(?P<sign>{SCOPE_SIGN})(?P<scope>\d+)"

    @staticmethod
    def extract_name(selector: str):
        return SemanticsUtils.separate_selector(selector)[0]

    @staticmethod
    def separate_selector(selector: str):
        matched = re.match(SemanticsUtils._selector_re(), selector).groupdict()
        return matched['name'], matched['sign'], matched['scope']

    @staticmethod
    def replace_selector_name(selector: str, new_name: str):
        name, sign, scope = SemanticsUtils.separate_selector(selector)
        return f'{new_name}{sign}{scope}'

    @staticmethod
    def displayable_time(t: int):
        return t if t >= 0 else EMPTY_TIME

    @staticmethod
    def create_empty_result(r: EvalResult):
        if isinstance(r, bool) or r == {} or list(r.values())[0] is None:
            raise TypeError('Cannot create an empty result.')
        return {q: None for q in list(r.values())[0][0]}, []

    @staticmethod
    def get_all_selectors(r: EvalResult):
        res = set()
        for t in r:
            res.update(r[t][0].keys())

        return res

    @staticmethod
    def _predicate(op):
        return f'lambda p1, p2: p1 {op} p2'

    @staticmethod
    def and_predicate():
        return SemanticsUtils._predicate('and')

    @staticmethod
    def raw_to_const_str(res: EvalResult):
        return list(list(res.values())[0][0].keys())[0]

    @staticmethod
    def get_first(times: Iterable[Time], res: EvalResult):
        return res[times[0]].values[0]


FALSE = lambda times: Const(False, times)
TRUE = lambda times: Const(True, times)
