import re
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass

import more_itertools

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import *

SemanticsArgType = Union[bool, EvalResult]


def first_satisfaction(formula: EvalResult) -> Union[int, bool]:
    for time in formula:
        result, replacements = formula[time]
        if result:
            return time

    return False


def last_satisfaction(formula: EvalResult) -> Union[int, bool]:
    return first_satisfaction({t: r for (t, r) in reversed(formula.items())})


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


class Operator(ABC):
    @abstractmethod
    def eval(self, *args):
        raise NotImplementedError()

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    def create_eval(self, *args):
        return lambda parser: self.eval(*[f(parser) for f in (args[2].asList())[0][1:]])


class UniLateralOperator(Operator):
    @abstractmethod
    def eval(self, arg):
        raise NotImplementedError()


class BiLateralOperator(Operator):
    @abstractmethod
    def eval(self, arg1, arg2):
        raise NotImplementedError()


class Globally(UniLateralOperator):
    @property
    def name(self):
        return "G"

    def eval(self, formula: SemanticsArgType):
        return Release().eval(False, formula)


class Release(BiLateralOperator):
    @property
    def name(self):
        return "R"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        return Not().eval(Until().eval(Not().eval(arg1), Not().eval(arg2)))


class Finally(UniLateralOperator):
    @property
    def name(self):
        return "F"

    def eval(self, arg: SemanticsArgType):
        return Until().eval(True, arg)


class Next(UniLateralOperator):
    @property
    def name(self):
        return "X"

    def eval(self, arg: SemanticsArgType):
        if arg is bool:
            """
            X(T) = T
            X(F) = F
            """
            return arg

        # TODO: Should I check for satisfaction? I.e., return {t:r for ... in ... ** if r[0] **} ??
        return {t: r for (t, r) in arg.items()[1::]}


class Until(BiLateralOperator):
    @property
    def name(self):
        return "U"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        if type(arg1) is bool and type(arg2) is bool:
            """
            U(T, T) = T
            U(T, F) = U(F, T) = F
            U(F, F) = F
            """
            return arg1 and arg2

        if type(arg1) is bool and type(arg2) is dict:
            if arg1:
                """
                U(T, ϕ) = ϕ 
                """
                return arg2

            """
            U(F, ϕ) = F
            """
            return False

        if type(arg1) is dict and type(arg2) is bool:
            if arg2:
                """
                ω ⊨ U(ϕ, T) ↔ ∃i >= 0, ω_i ⊨ ϕ  
                """
                return {t: r for (t, r) in arg1.items() if t >= first_satisfaction(arg1)}

            return False

        # Both formulas are of type EvalResult:
        """
        ω ⊨ U(ϕ, ψ) ↔ ∃i >= 0, ω_i ⊨ ψ ∧ ∀ <= 0 k <= i, ω_k ⊨ ϕ  
        """
        formula2_first_satisfaction = first_satisfaction(arg2)
        if not formula2_first_satisfaction:
            return False

        return {t: r1 for (t, r1) in arg1.items() if t <= formula2_first_satisfaction and r1[0]}


class Or(BiLateralOperator):
    @property
    def name(self):
        return "∨"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        if type(arg1) is bool and type(arg2) is bool:
            return arg1 or arg2

        if type(arg1) is bool and type(arg2) is dict:
            if arg1:
                return True

            return arg2

        if type(arg1) is dict and type(arg2) is bool:
            if arg2:
                return True

            return arg1

        return {t: (r1[0] or r2[0], r1[1] + r2[1]) for t, r1 in arg1.items() for t2, r2 in arg2.items() if t == t2}


class Not(UniLateralOperator):
    @property
    def name(self):
        return "N"

    def eval(self, arg: SemanticsArgType):
        if type(arg) is bool:
            return not arg

        return {t: (not r[0], r[1]) for (t, r) in arg.items()}


class And(BiLateralOperator):
    @property
    def name(self):
        return "∧"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        return Not().eval(Or().eval(Not().eval(arg1), Not().eval(arg2)))


class Before(BiLateralOperator):
    @property
    def name(self) -> str:
        return "B"

    def eval(self, arg1, arg2):
        return Until().eval(Not().eval(Globally().eval(Not().eval(arg1))), arg2)


class After(BiLateralOperator):
    @property
    def name(self) -> str:
        return "A"

    def eval(self, arg1, arg2):
        return Before().eval(arg2, arg1)


class AllFuture(UniLateralOperator):
    @property
    def name(self) -> str:
        return "₣"

    def eval(self, arg):
        return Globally().eval(Next().eval(arg))


class First(UniLateralOperator):

    @property
    def name(self) -> str:
        return "Q"

    def eval(self, arg: SemanticsArgType):
        if type(arg) is bool:
            """
                Q(T) = T
                Q(F) = F
            """
            return arg

        first = min(filter(lambda k: arg[k][0] != False, arg))
        if not first:
            return False

        return {first: arg[first]}


class Last(UniLateralOperator):

    @property
    def name(self) -> str:
        return "Z"

    def eval(self, arg):
        if type(arg) is bool:
            return arg

        first = max(filter(lambda k: arg[k][0] != False, arg))
        if not first:
            return False

        return {first: arg[first]}


class Where(BiLateralOperator):

    @property
    def name(self) -> str:
        return "W"

    def eval(self, selector, condition):
        """
        :param selector:  Select clause.
        :param condition: Where clause.
        :return:
        """
        if isinstance(condition, bool):
            if condition:
                return selector

            # TODO: Should be False?
            return {}

        # condition[t][0] is a dict in the form: {"query": <result **SHOULD BE** True/False>}.
        # Therefore the filter part of this dict comp. verifies that every "query" in condition[t][0] is set to True.
        return {k: v for k, v in selector.items() if all([*condition[k][0].values()])}


class SetUnion(BiLateralOperator):

    @property
    def name(self) -> str:
        return "++"

    def eval(self, arg1: EvalResult, arg2: EvalResult):
        if isinstance(arg1, bool) or isinstance(arg2, bool):
            raise TypeError("Cannot run Union if any of its operands are bool.")

        return {k1: ({**res1, **res2}, rep1 + rep2) for (k1, (res1, rep1)), (k2, (res2, rep2)) in
                zip(arg1.items(), arg2.items()) if k1 == k2}


class Align(BiLateralOperator):
    @dataclass
    class AlignmentHeuristic(object):
        func: Callable
        pattern: str

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs), self.pattern

    ALIGNMENT_HEURISTICS = [
        AlignmentHeuristic(lambda r1, r2: lambda r: r, 'r -> r'),
        AlignmentHeuristic(lambda r1, r2: lambda r: r - (r2 - r1), 'r - r1'),
        AlignmentHeuristic(lambda r1, r2: lambda r: r * (r2 / r1), 'r * (r / r1)')
    ]

    def __init__(self):
        super(BiLateralOperator, self).__init__()

        self._heuristic_iterator = iter(Align.ALIGNMENT_HEURISTICS)
        self._current_heuristic = None

    def next_heuristic(self, r1, r2):
        if self._current_heuristic != Align.ALIGNMENT_HEURISTICS[1]:
            self._current_heuristic = next(self._heuristic_iterator)

        return self._current_heuristic(r1, r2)

    @property
    def name(self) -> str:
        return "Align"

    def eval(self, r1: SemanticsArgType, r2: SemanticsArgType):
        if isinstance(r1, bool) or isinstance(r2, bool):
            raise TypeError("Cannot run Align if any of its operands are bool.")

        r1_selectors, r2_selectors = SemanticsUtils.selectors(r1), SemanticsUtils.selectors(r2)

        all_selectors = list(r1_selectors) + list(r2_selectors)
        results = {k: ({k: None for k in all_selectors}, []) for k in SemanticsUtils.joined_times(r1, r2)}

        r1_clipped = SemanticsUtils.remove_none_prefix(r1)
        r2_clipped = SemanticsUtils.remove_none_prefix(r2)

        heuristic, heuristic_pattern = self.next_heuristic(None, None)

        for s1, s2 in zip(r1_selectors, r2_selectors):
            assert SemanticsUtils.extract_name(s1) == SemanticsUtils.extract_name(s2)
            for t1, t2 in zip(r1_clipped, r2_clipped):
                res1 = r1[t1][0][s1]
                res2 = heuristic(r2[t2][0][s2])
                updated_results = {s1: res1, s2: res2}

                # The values are the same.
                if res1 != res2:
                    # There is a difference between the values of the selector of r1 and r2.
                    # Create a heuristic with both values.
                    heuristic, heuristic_pattern = self.next_heuristic(res1, res2)
                    updated_results[SemanticsUtils.replace_selector_name(s2, heuristic_pattern)] = heuristic(res2)

                results[t1][0].update(**updated_results)
                results[t1][1].extend(set(results[t1][1]).union(r1[t1][1]).union(r2[t1][1]))

        return results


class Meld(BiLateralOperator):

    @property
    def name(self) -> str:
        return "Meld"

    @dataclass
    class _MeldData(object):
        data: Tuple[Any]
        time: int
        comp_data: Tuple[Any]
        replacements: List

        def __eq__(self, o: 'Meld._MeldData') -> bool:
            if not isinstance(o, Meld._MeldData):
                return False

            return self.comp_data == o.comp_data

        @classmethod
        def empty(cls):
            return cls(tuple(), -1, tuple(), [])

    def eval(self, r1, r2):
        if isinstance(r1, bool) or isinstance(r2, bool):
            raise TypeError("Cannot run Meld if any of its operands are bool.")

        r1_selectors, r2_selectors = SemanticsUtils.selectors(r1), SemanticsUtils.selectors(r2)

        # Make sure that the user has requested for the same selectors.
        r1_selectors_no_scope = [SemanticsUtils.extract_name(s) for s in r1_selectors]
        r2_selectors_no_scope = [SemanticsUtils.extract_name(s) for s in r2_selectors]

        assert r1_selectors_no_scope == r2_selectors_no_scope

        results = {}

        r1_clipped = SemanticsUtils.remove_none_prefix(r1)
        r2_clipped = SemanticsUtils.remove_none_prefix(r2)

        res1 = [Meld._MeldData(
            data=tuple(r1[t][0][s] for s in r1_selectors),
            time=t,
            comp_data=tuple(r1[t][0][s] for s in r1_selectors),
            replacements=r1[t][1]
        ) for t in r1_clipped]

        res2 = [Meld._MeldData(
            data=tuple(r2[t][0][s] for s in r2_selectors),
            time=t,
            comp_data=tuple(r2[t][0][s] for s in r2_selectors),
            replacements=r2[t][1]
        ) for t in r2_clipped]

        indices = Meld._create_indices(res1, res2)

        prev1 = prev2 = None
        empty = Meld._MeldData.empty()
        for i1, i2 in indices:
            r1 = res1[i1] if i1 != prev1 else empty
            r2 = res2[i2] if i2 != prev2 else empty

            prev1, prev2 = i1, i2

            d = dict(list(zip(r1_selectors, r1.data + ('-',) * len(r1_selectors))) + list(
                zip(r2_selectors, r2.data + ('-',) * len(r2_selectors))))

            results[SemanticsUtils.displayable_time(r1.time),
                    SemanticsUtils.displayable_time(r2.time)] = (d, set(r1.replacements).union(r2.replacements))

        return results

    @staticmethod
    def _create_indices(a1: List['_MeldData'], a2: List['_MeldData']):
        diff_mat = Meld._create_diff_mat(a1, a2)
        reversed_indices = []
        i, j = len(a1) - 1, len(a2) - 1
        while i > 0 and j > 0:
            i, j = diff_mat[i][j][1]
            reversed_indices.append((i, j))

        if i > 0:
            # TODO: Deal with i > 0 and with j > 0
            reversed_indices.extend([])
        return reversed(reversed_indices)

    @staticmethod
    def _create_diff_mat(a1: List['_MeldData'], a2: List['_MeldData']):
        deletion_weight = insert_weight = 1

        diff_mat = [[(0, (-1, -1))] * (len(a2) + 1) for _ in [*a1, None]]

        for i in range(len(a1)):
            for j in range(len(a2)):
                if j == 0:
                    diff_mat[i][j] = (i * deletion_weight, (-1, -1))

                elif i == 0:
                    diff_mat[i][j] = (j * insert_weight, (-1, -1))

                else:
                    if a1[i] == a2[j]:
                        diff_mat[i][j] = (diff_mat[i - 1][j - 1][0], (i - 1, j - 1))
                    else:
                        del_price = diff_mat[i - 1][j][0] + deletion_weight
                        ins_price = diff_mat[i][j - 1][0] + insert_weight

                        diff_mat[i][j] = (del_price, (i - 1, j)) if del_price < ins_price else (ins_price, (i, j - 1))

        return diff_mat


class NextAfter(BiLateralOperator):
    @property
    def name(self) -> str:
        return "NA"

    def eval(self, a: EvalResult, b: EvalResult):
        if isinstance(a, bool) or isinstance(b, bool):
            raise TypeError('Cannot find NextAfter if either of the queries are bool')

        replacements_times = lambda er: [t for t in er if any(rep.time == t for rep in er[t][1])]

        a_times = replacements_times(a)
        b_times = replacements_times(b)

        time_ranges = zip(a_times, a_times[1::])
        b_relevant_keys = list(
            map(lambda time_range: next((t for t in b_times if t in range(*time_range)), None), time_ranges))

        """{t:r for t, r in b.items() if t in list( map(lambda time_range: next((t for t in [t for t in b if any(
        rep.time == t for rep in b[t][1])] if t in range(*time_range)), None), list(zip([t for t in a if any(rep.time 
        == t for rep in a[t][1])], [t for t in a if any(rep.time == t for rep in a[t][1])][1::]))))} """
        return {t: r if t in b_relevant_keys else SemanticsUtils.create_empty_result(b) for (t, r) in b.items()}


UniLateralOperator.ALL = UniLateralOperator.__subclasses__()
BiLateralOperator.ALL = BiLateralOperator.__subclasses__()
Operator.ALL = UniLateralOperator.ALL + BiLateralOperator.ALL