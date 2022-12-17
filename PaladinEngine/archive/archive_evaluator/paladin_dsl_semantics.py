import abc
import collections.abc
import functools
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce
from itertools import product

import more_itertools

from archive.archive import Archive, Rk, Rv
from archive.archive_evaluator.archive_evaluator import ArchiveEvaluator
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import *
from ast_common.ast_common import *
from common.common import IS_ITERABLE
from stubs.stubs import __AS__

SemanticsArgType = Union[bool, EvalResult]
Time = int


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


@dataclass
class Operator(ABC):

    def __init__(self, times: Optional[Iterable[Time]] = None):
        self._times = times

    def eval(self, archive: Optional[Archive] = None,
             query_locals: Optional[Dict[str, EvalResult]] = None) -> EvalResult:
        raise NotImplementedError()

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    # @abstractmethod
    # def create_eval(self, archive: Optional[Archive] = None, *args):
    #     # *[(f, parser) for f in (args[2].asList())[0][1:]]
    #     return self.eval

    @property
    def times(self):
        if isinstance(self._times, range):
            return self._times

        # Assuming here that _times is an iterable of ranges.
        if IS_ITERABLE(self._times):
            return reduce(lambda times, rng: times + list(rng), self._times, [])

        return self._times

    @times.setter
    def times(self, value):
        self._times = value

    def _get_args(self) -> Collection['Operator']:
        raise NotImplementedError()

    def update_times(self, times) -> 'Operator':
        self.times = times

        for a in self._get_args():
            a.times = times
            a.update_times(times)

        return self

    @classmethod
    def all(cls) -> List[Type['Operator']]:
        return functools.reduce(lambda res, sub: res + sub._all(), cls.__subclasses__(), [])

    @classmethod
    def _all(cls):
        return cls.__subclasses__()


class UniLateralOperator(Operator, ABC):
    """
        Tagging class.
    """

    def __init__(self, times: Iterable[Time], first: Operator):
        super(UniLateralOperator, self).__init__(times)
        self.first = first

    def _get_args(self) -> Collection['Operator']:
        return [self.first]


class BiLateralOperator(Operator, ABC):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        super(BiLateralOperator, self).__init__(times)
        self.first: Operator = first
        self.second: Operator = second

    def _get_args(self) -> Collection['Operator']:
        return [self.first, self.second]


class TriLateralOperator(Operator, ABC):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator, third: Operator):
        super(TriLateralOperator, self).__init__(times)
        self.first: Operator = first
        self.second: Operator = second
        self.third: Operator = third

    def _get_args(self) -> Collection['Operator']:
        return [self.first, self.second, self.third]


class VariadicLateralOperator(Operator, ABC):
    def __init__(self, times: Iterable[Time], *args: List[Operator]):
        super(VariadicLateralOperator, self).__init__(times)
        self.args: List[Operator] = args

    def _get_args(self) -> Collection['Operator']:
        return self.args


class Raw(Operator):

    def __init__(self, query: str, line_no: Optional[int] = -1,
                 times: Optional[Iterable[Time]] = None):
        Operator.__init__(self, times)
        self.query = query
        self.line_no = line_no

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        # Extract names to resolve from the archive.
        extractor = ArchiveEvaluator.SymbolExtractor()
        extractor.visit(str2ast(self.query))

        # Split query into sub queries.
        queries = split_tuple(self.query)

        results = []

        for t in self.times:
            resolved_names = Raw._resolve_names(archive, extractor.names, self.line_no, t, query_locals)
            resolved_attributes = Raw._resolve_attributes(archive, extractor.attributes, self.line_no, t,
                                                          query_locals)

            replacer = ArchiveEvaluator.SymbolReplacer(resolved_names, resolved_attributes, t)
            try:
                # TODO: Can AST object be compiled and then evaled (without turning to string)?
                result = eval(ast2str(replacer.visit(ast.parse(self.query))))
                if not isinstance(result, Iterable):
                    result = (result,)
            except IndexError:
                result = [None] * len(queries)
            except KeyError:
                result = [None] * len(queries)
            results.append(EvalResultEntry(t,
                                           [EvalResultPair(self.create_key(q), r) for q, r in zip(queries, result)]
                                           if len(queries) > 1
                                           else [EvalResultPair(self.create_key(self.query), result)],
                                           replacer.replacements))

        return EvalResult(results)

    def create_key(self, query: str):
        return f'{query}{SCOPE_SIGN}{self.line_no}' if self.line_no is not None and self.line_no != -1 else f'{query}'

    @staticmethod
    def _resolve_names(archive: Archive, names: Set[str], line_no: int, time: int,
                       query_locals: Dict[str, EvalResult]) -> ExpressionMapper:
        """
            Resolves the values of the objects in names from the archive.
        :param names: A set of names to resolve.
        :param line_no: The line no in which to look for the scope of the object.
        :param time: The time in which the object's value should be resolved.
        :return:
        """

        resolved = {name: archive.find_by_line_no(name, line_no, time)[name] for name in names}
        if query_locals:
            resolved.update({name: query_locals[name][time].value for name in names if name in query_locals})

        return resolved

    @staticmethod
    def _resolve_attributes(archive: Archive, attributes: Set[str], line_no: int, time: int,
                            query_locals: Dict[str, EvalResult]) -> ExpressionMapper:
        resolved = {attr: archive.find_by_line_no(attr, line_no, time)[attr] for attr in attributes}

        if query_locals:
            for attr in attributes:
                attr_base = attr.split('.')[0]
                if attr_base in query_locals:
                    resolved[attr] = query_locals[time][attr_base].value

        return resolved

    def _get_args(self) -> Collection['Operator']:
        return []


class Const(Operator):
    CONST_KEY = 'CONST'

    def __init__(self, const, times: Iterable[Time] = None):
        super(Const, self).__init__(times if times else [range(0, 1)])
        self.const = const

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return EvalResult([EvalResultEntry(t, [EvalResultPair(Const.CONST_KEY, self.const)], []) for t in self.times])

    def _get_args(self) -> Collection['Operator']:
        return []


FALSE = Const(False)
TRUE = Const(True)


class Globally(UniLateralOperator):
    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Release(self.times, FALSE, self.first).eval(archive)


class Release(BiLateralOperator):

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Not(self.times, Until(self.times, Not(self.times, self.first), Not(self.times, self.second))).eval(
            archive)


class Finally(UniLateralOperator):
    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Until(self.times, TRUE, self.first).eval(archive)


class Next(UniLateralOperator):
    """
        Next(<c>): Returns the second satisfaction of <c> (next after first)
    """

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        formula_result = self.first.eval(archive)
        if formula_result is bool:
            """
            Next(T) = T
            Next(F) = F
            """
            return formula_result

        first = formula_result.first_satisfaction()

        return [r if r.time != first.time else r.create_const_copy(False) for r in formula_result]


class Until(BiLateralOperator):

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(archive)
        second = self.second.eval(archive)

        if type(first) is bool and type(second) is bool:
            """
            U(T, T) = T
            U(T, F) = U(F, T) = F
            U(F, F) = F
            """
            return first and second

        if isinstance(first, bool) and not isinstance(second, bool):
            if first:
                """
                U(T, ϕ) = ϕ 
                """
                return second

            """
            U(F, ϕ) = F
            """
            return False

        if not isinstance(first, bool) and isinstance(second, bool):
            if second:
                """
                ω ⊨ U(ϕ, T) ↔ ∃i >= 0, ω_i ⊨ ϕ  
                """
                return [r for r in first if r.time >= first.first_satisfaction().time]

            return False

        # Both formulas are of type EvalResult:
        """
        ω ⊨ U(ϕ, ψ) ↔ ∃i >= 0, ω_i ⊨ ψ ∧ ∀ <= 0 k <= i, ω_k ⊨ ϕ  
        """
        formula2_first_satisfaction = second.first_satisfaction()
        if not formula2_first_satisfaction:
            return False

        return [r for r in first if r.time <= formula2_first_satisfaction.time and r.satisfies()]


class Or(BiLateralOperator):

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(archive)
        second = self.second.eval(archive)

        if isinstance(first, bool) and isinstance(second, bool):
            return first or second

        if isinstance(first, bool) and isinstance(second, EvalResult):
            if first:
                return True

            return second
        if isinstance(first, EvalResult) and isinstance(second, bool):
            if second:
                return True

            return first

        #
        # FIXME: How do boolean operators fit in the DSL? What is the meaning of
        #        Or('x': 1, 'y': 2)?
        return []
        # return [EvalResult([EvalResultEntry(e1.time, [EvalResultPair(e)]) for e1 in first for e2 in second])]
        # return {t: (r1[0] or r2[0], r1[1] + r2[1]) for t, r1 in first.items() for t2, r2 in second.items() if t == t2}


class Not(UniLateralOperator):

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(archive)
        if isinstance(first, bool):
            return not first

        # FIXME: See note in Or
        # return {t: ({k: not v[0][k] if v[0][k] is not None else None for k in v[0]}, v[1]) for t, v in first.items()}
        return []


class And(BiLateralOperator):
    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Not(self.times, Or(self.times, Not(self.times, self.first), Not(self.times, self.second))).eval(archive)


class Before(BiLateralOperator):

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Until(self.times, Not(self.times, Globally(self.times, Not(self.times, self.first))), self.second).eval(
            archive)


class After(BiLateralOperator):

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Before(self.times, self.second, self.first).eval(archive)


class AllFuture(UniLateralOperator):
    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Globally(self.times, Next(self.times, self.first))


class First(UniLateralOperator):
    """
        First(<c>): Selects <c> in the first time it exists.
    """

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(archive)

        first_result = first.first_satisfaction()
        if not first_result:
            return EvalResult.EMPTY()

        return EvalResult([first_result])


class Last(UniLateralOperator):
    """
        Last(<c>): Selects <c> in the last time it has a value.
    """

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(archive)
        return EvalResult([first.last_satisfaction()])


class Where(BiLateralOperator):
    """
        Where(<selector>, <condition>): Selects <selector> in all times the <condition> is met.
    """

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        condition: EvalResult = self.second.eval(archive)

        # Set times for selector with the results given by condition's eval.
        self.first.update_times(condition.satisfaction_ranges())

        # Create a sparse results-list with the original time range.
        first_results = self.first.eval(archive)

        return EvalResult(
            [first_results[time] if time in self.first.times else EvalResultEntry.empty(time)
             for time in self.times
             ]
        )


class Union(VariadicLateralOperator):
    """
        Union(<c1>, <c2>, ..., <ck>): Selects <c>'s together.
    """

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return reduce(lambda r1, r2: EvalResult.join(r1, r2),
                      map(lambda arg: arg.eval(archive, query_locals), self.args),
                      EvalResult.EMPTY)


class Align(BiLateralOperator):
    """
        Align(<c1>, <c2>): Selects <c1> and <c2> by aligning them using heuristics.
    """

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

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        r1 = self.first.eval(archive)
        r2 = self.second.eval(archive)

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
    """
        Meld(<c1>, <c2>): Align <c1> and <c2> using meld algorithm
    """

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

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        r1 = self.first.eval(archive)
        r2 = self.second.eval(archive)

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
    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        a = self.first.eval(archive)
        b = self.second.eval(archive)

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


class TimeOperator(Operator):
    TIME_KEY = 'time'

    def __init__(self, op: Operator):
        super().__init__(op.times)
        self.op = op

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        results = self.op.eval(archive)
        return EvalResult(
            [EvalResultEntry(e.time, [EvalResultPair(TimeOperator.TIME_KEY, e.satisfies())], []) for e in results])

    def _get_args(self) -> Collection['Operator']:
        return [self.op]


class TimeFilter(BiLateralOperator):
    """
        TimeFilter(<c1>,<c2>): Creates a time window of times t in which t ⊨ <c1> and t ⊨ <c2>
    """

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = TimeOperator(self.first).eval(archive)
        second = TimeOperator(self.second).eval(archive)

        results = []
        for t in set(first.ti).union(second.keys()):
            satisfaction = satisfies(first, t) and satisfies(second, t)
            replacements = list(set(first[t][1] + second[t][1]))
            results[t] = {TimeOperator.TIME_KEY: satisfaction}, replacements

        return results

    def eval_ranges(self):
        filtered_times = self.eval(archive)
        if not filtered_times:
            return []

        ranges = []
        range_start = None
        range_end = range_start
        for t in sorted(filtered_times.keys()):
            if satisfies(filtered_times, t):
                if not range_start:
                    range_start = t
                else:
                    range_end = t
            else:
                if range_start:
                    ranges.append(range(range_start, range_end))
                    range_start = range_end = None

        if range_start and range_end:
            ranges.append(range(range_start, range_end))

        if range_start and not range_end:
            ranges.append((range(range_start, range_start + 1)))
        return ranges


class VarSelector(UniLateralOperator):
    """
        VarSelector(<time_range>): Selects all vars that were changed in a time range.
    """

    VARS_KEY = 'vars'

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        results = []
        for time_range in self.first.eval(archive).satisfaction_ranges():
            v = self._get_all_vars(archive, time_range)

            results.extend([EvalResultEntry(t, [EvalResultPair(VarSelector.VARS_KEY, v)], []) for t in time_range])

        return EvalResult(results)

    def _get_all_vars(self, archive: Archive, time_range: range):
        assignments = archive.get_all_assignments_in_time_range(time_range.start, time_range.stop)
        # TODO: re.match("<class '.*'>", ...) is a patch for not showing the automatic __AS__ of inner fields.
        # FIXME: Add "kind" to each __AS__ with "var" or "automatic" for inner fields etc.
        return list(
            set(filter(lambda v: not re.match("<class '.*'>|__.*", v) and not '[' in v, map(lambda r: r[1].expression, assignments))))


class Diff(BiLateralOperator):
    """
          Diff(<selector>, <cond>): Selects <selector> when <cond> and t-1 before <cond>
    """

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        time_range = self.second.eval(archive)
        selector_results = {}
        for r in satisfaction_ranges(time_range):
            self.update_times([r])
            tr = range(r.start - 1, r.start)
            before_first_results = Where(times=tr, first=self.first.update_times([tr]), second=TRUE).eval(archive)
            self.update_times([r])
            selector_results.update(before_first_results)
            selector_results.update(Where(self.times, self.first, self.second).eval(archive))

        return selector_results


class LoopIteration(BiLateralOperator):
    """
    LoopIteration(<i>, <v>): Shows changes that have taken place in a loop where its iterator <i> had a value (<v>).
                             ** i, v ** must be a Raw operators, i.e. [[ ... ]] or [[ ... ]]@...
    """

    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        BiLateralOperator.__init__(self, times, first, second)

    # noinspection PyTypeChecker
    @property
    def _iterator_equals_value(self):
        iterator: Raw = self.first
        value: Raw = self.second
        return Raw(f'{iterator.query} == {value.query}', iterator.line_no, self.times).eval(archive)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        if not isinstance(self.first, Raw) or not isinstance(self.second, Raw):
            raise TypeError('iterator and its value must be Raw operators')

        relevant_times = TimeFilter(self.times, self._iterator_equals_value, self._iterator_equals_value).eval_ranges()

        self.update_times(relevant_times)

        changed_vars_selector = VarSelector(archive, self.times, self.first, self.first)

        changed_vars_selector_result = changed_vars_selector.eval(archive)
        if len(changed_vars_selector_result) == 0:
            return {}

        changed_vars = list(changed_vars_selector_result.values())[0][0][VarSelector.VARS_KEY]
        changed_vars_diffs = []
        for v in sorted(changed_vars):
            ###
            # FIXME: The var is not located using a specific scope in here (line_no=-1)
            #  therefore other vars can get in the way...
            #  For example:
            #  ```
            #   1: for i in range(1,4):
            #      j = 1
            #      ...
            #   10: for i in range(5,8):
            #     ...
            #  ```
            #  If We look for the first iter of the second loop (i == 5), with LoopIteration([[i]]@10, [[5]]),
            #  the last value of the first iteration (i@1 == 4) will also be presented.
            #  There is Currently a trouble to fix this, because i have a scope (i@10) but after the VarSelection,
            #  j@10 is incorrect.
            #
            #  TODO: Maybe if a range of lines that compound the loop is used, a range of scopes can be used:
            #   E.g.: LoopIteration([[i]], [[0]], 1, 10)
            ###
            selector = Raw(archive, v, times=self.times)
            changed_var_diff = Where(self.times, selector, self._iterator_equals_value)
            changed_vars_diffs.append(changed_var_diff)
            # x = changed_var_diff.eval(archive)
            # print(x)

        return Union(self.times, *changed_vars_diffs).eval(archive)


class LoopSummary(UniLateralOperator):
    """
        LoopSummary(<line>): Creates a summary of a loop which header (for i in ...) is in <line>
                             ** <line> should be a Raw Operator, i.e. [[<line>]]
    """

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = int(SemanticsUtils.raw_to_const_str(self.first.eval(archive)))

        assignments_by_line_no: Dict[Rk, List[Rv]] = archive.filter(
            [lambda rv: rv.line_no == line_no, lambda rv: rv.key.stub_name == __AS__.__name__])

        res = {}
        for rk, lrv in assignments_by_line_no.items():
            iterator = Raw(archive, rk.field, line_no, self.times)
            for rv in filter(lambda rv: rv.line_no == line_no, lrv):
                li = LoopIteration(archive, self.times, iterator, Raw(archive, rv.value, line_no, self.times))
                res.update({t: r for (t, r) in li.eval(archive).items() if t <= rv.time})

        return res


class Line(UniLateralOperator):
    """
        Line(<number>): Returns values of all objects that existed when the program hit line numbered <number>
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))

    def eval(self, archive: Optional[Archive] = None,
             query_locals: Optional[Dict[str, EvalResult]] = None) -> EvalResult:
        line_no = self.first.eval(archive)[0].values[0]
        events_by_line_no: List[Tuple[Rk, Rv]] = archive.find_events(line_no)
        if not events_by_line_no:
            return EvalResult.empty(self.times)

        event_times = list(map(lambda t: t[1].time, events_by_line_no))
        event_times = event_times if event_times[0] == 0 else [0] + event_times
        ranges = [(t1, t2) for t1, t2 in zip(event_times, event_times[1::])]
        results = EvalResult.empty(self.times)

        for r in ranges:
            time_range = range(r[0], r[1] + 1)
            vars = VarSelector(self.times, Const(True, times=time_range)).eval(archive)
            if not vars:
                continue

            for v in vars[r[1]].__getitem__(VarSelector.VARS_KEY).value:
                results = results.join(results, Raw(v, None, time_range).eval(archive))

        return results
