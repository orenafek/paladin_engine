import re
from abc import ABC
from math import floor

import more_itertools
import frozendict

from archive.archive import Archive, Rk, Rv
from archive.archive_evaluator.archive_evaluator import ArchiveEvaluator
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import *
from ast_common.ast_common import *

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
        result = []
        for t in self._times:
            if isinstance(t, range):
                result.extend(list(t))

            elif isinstance(t, Time):
                result.append(t)

            else:
                raise TypeError(f'A weird time of type {type(t)}')

        return result

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
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            subclasses.extend(subclass.all())

        return list(set(subclasses))

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
                result = eval(ast2str(replacer.visit(ast.parse(self.query))), EVAL_BUILTIN_CLOSURE)
            except (IndexError, KeyError, NameError):
                result = [None] * len(queries) if len(queries) > 1 else None

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

        # Delete empty results (for names that couldn't be found).
        resolved = {name: resolved[name] for name in resolved if resolved[name]}

        if query_locals:
            resolved.update({name: query_locals[name][time].value for name in names if name in query_locals})

        return resolved

    @staticmethod
    def _resolve_attributes(archive: Archive, attributes: Set[str], line_no: int, time: int,
                            query_locals: Dict[str, EvalResult]) -> ExpressionMapper:

        resolved = {attr: archive.find_by_line_no(attr, line_no, time)[attr] for attr in attributes}
        # Delete empty results (for names that couldn't be found).
        resolved = {name: resolved[name] for name in resolved if resolved[name]}

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


class TimeOperator(Operator, ABC):
    TIME_KEY = '__TIME'

    @classmethod
    def make(cls, op: Operator):
        return op if isinstance(op, TimeOperator) else Whenever(op.times, op)

    def __init__(self, times: Iterable[Time]):
        super().__init__(times)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        raise NotImplementedError()

    def _get_args(self) -> Collection['Operator']:
        return [self.op]

    @staticmethod
    def create_time_eval_result_entry(t: Time, res: bool,
                                      rep: Optional[List[Replacement]] = None) -> EvalResultEntry:
        return EvalResultEntry(t, [EvalResultPair(TimeOperator.TIME_KEY, res)], rep if rep else [])


class Whenever(VariadicLateralOperator, TimeOperator):

    def __init__(self, times: Iterable[Time], *args: Operator):
        VariadicLateralOperator.__init__(self, times, *args)
        TimeOperator.__init__(self, times)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        evaled_args = list(map(lambda arg: arg.eval(archive, query_locals), self.args))
        arg_results = list(map(lambda er: lambda t: er[t].satisfies(), evaled_args))

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, all([arg_res(t) for arg_res in arg_results]),
                                                       list(reduce(lambda l, rep: l + rep,
                                                                   map(lambda ar: ar[t].replacements, evaled_args),
                                                                   [])))
            for t in self.times
        ])


class ConstTime(TimeOperator):

    def __init__(self, times: Iterable[Time], const_time: int):
        super().__init__(times)
        self.const_time = const_time

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t == self.const_time, [])
            for t in self.times
        ])


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


class BiTimeOperator(BiLateralOperator, TimeOperator, ABC):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator,
                 bi_result_maker: Callable[[bool, bool], bool]):
        BiLateralOperator.__init__(self, times, first, second)
        TimeOperator.__init__(self, times)
        self.bi_result_maker = bi_result_maker

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = TimeOperator.make(self.first).eval(archive, query_locals)
        second = TimeOperator.make(self.second).eval(archive, query_locals)

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(e1.time, self._make_res(e1, e2),
                                                       e1.replacements + e2.replacements)

            for e1, e2 in zip(first, second)])

    def _make_res(self, e1: EvalResultEntry, e2: EvalResultEntry) -> bool:
        return self.bi_result_maker(e1[TimeOperator.TIME_KEY].value, e2[TimeOperator.TIME_KEY].value)


class Until(BiLateralOperator, TimeOperator):

    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        BiLateralOperator.__init__(self, times, first, second)
        TimeOperator.__init__(self, times)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = Whenever(self.times, self.first).eval(archive, query_locals)
        second = self.second.eval(archive, query_locals)
        not_second = Not(self.times, self.second).eval(archive, query_locals)

        min_max_times = range(first.first_satisfaction().time,
                              min(second.last_satisfaction().time + 1, self.times.stop))

        # Both formulas are of type EvalResult:
        """
        ω ⊨ U(ϕ, ψ) ↔ ∃i >= 0, ω_i ⊨ ψ ∧ ∀ <= 0 k <= i, ω_k ⊨ ϕ  
        """
        return EvalResult(
            [TimeOperator.create_time_eval_result_entry(t,
                                                        False
                                                        if t not in min_max_times
                                                        else first[t].satisfies() and not_second[t].satisfies())
             for t in self.times])


class Range(BiLateralOperator, TimeOperator):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        BiLateralOperator.__init__(self, times, first, second)
        TimeOperator.__init__(self, times)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(archive, query_locals)
        second = self.second.eval(archive, query_locals)

        first_satisfaction = first.first_satisfaction().time
        last_satisfaction = second.last_satisfaction().time

        if first_satisfaction < 0 or last_satisfaction < 0:
            return EvalResult.empty(self.times)

        min_max_times = range(first_satisfaction, min(last_satisfaction + 1, self.times.stop))

        return EvalResult([TimeOperator.create_time_eval_result_entry(t, t in min_max_times) for t in self.times])


class Or(BiTimeOperator):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        super().__init__(times, first, second, lambda r1, r2: r1 or r2)


class And(BiTimeOperator):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        super().__init__(times, first, second, lambda r1, r2: r1 and r2)


class Not(UniLateralOperator, TimeOperator):

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = Whenever(self.times, self.first).eval(archive, query_locals)

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, not first[t].satisfies(), first[t].replacements)
            for t in self.times])


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


class VarSelector(UniLateralOperator):
    """
        VarSelector(<time_range>): Selects all vars that were changed in a time range.
    """

    VARS_KEY = 'vars'

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        return EvalResult([
            EvalResultEntry(t, [
                EvalResultPair(VarSelector.VARS_KEY, self._get_all_vars(archive, time_range))], [])
            for time_range in self.first.eval(archive, query_locals).satisfaction_ranges() for t in time_range
        ])

    def _get_assignments(self, archive: Archive, time_range: range):
        return archive.get_assignments(time_range=time_range)

    def _get_all_vars(self, archive: Archive, time_range: range) -> Iterable[str]:
        return {vv.expression for k, vv in self._get_assignments(archive, time_range)}

class VarSelectorByTimeAndLines(VarSelector):
    def __init__(self, times: Iterable[Time], time: Operator, lines: range):
        super().__init__(times, time)
        self.lines = lines

    def _get_assignments(self, archive: Archive, time_range: range):
        return archive.get_assignments(time_range=time_range, line_no_range=self.lines)


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
    LoopIteration(<ln>, <i>): Shows changes that have taken place in a loop in row <ln> in its <i>'th index.
                             ** i, v ** must be numbers.
    """

    def __init__(self, times: Iterable[Time], line_no: int, index: int):
        BiLateralOperator.__init__(self, times, Const(line_no, times), Const(index, times))

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = self.first.eval(archive)[self.times[0]].values[0]
        index: int = self.second.eval(archive)[self.times[0]].values[0]

        loop_iteration_starts_and_ends: List[Tuple[Rk, Rv]] = sorted(archive.get_loop_iterations(line_no),
                                                                     key=lambda t: t[1].time)
        if index * 2 > len(loop_iteration_starts_and_ends) or index * 2 + 1 > len(loop_iteration_starts_and_ends):
            return EvalResult.empty(self.times)

        loop_iteration_start = loop_iteration_starts_and_ends[index * 2]
        loop_iteration_end = loop_iteration_starts_and_ends[index * 2 + 1]
        iterator_values_times = Range(self.times,
                                      ConstTime(self.times, loop_iteration_start[1].time),
                                      ConstTime(self.times, loop_iteration_end[1].time))

        return Union(self.times, *self._create_iterations_operators(iterator_values_times, archive, query_locals,
                                                                    range(loop_iteration_start[1].line_no,
                                                                          loop_iteration_end[1].line_no + 1))) \
            .eval(archive, query_locals)

    def _create_iterations_operators(self, time_range_operator: Range, archive: Archive,
                                     query_locals: Optional[Dict[str, EvalResult]],
                                     line_no_range: range) -> Iterable[Operator]:
        vars_selector_result = VarSelectorByTimeAndLines(self.times, time_range_operator, line_no_range).eval(archive,
                                                                                                              query_locals)

        if len(vars_selector_result) == 0:
            return EvalResult.empty(self.times)

        changed_vars = list(vars_selector_result)[0][VarSelector.VARS_KEY].value
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
            selector = Raw(v, times=self.times)
            changed_vars_diffs.append(Where(self.times, selector, time_range_operator))

        return changed_vars_diffs


class LoopSummary(UniLateralOperator):
    """
        LoopSummary(<line>): Creates a summary of a loop which header (for i in ...) is in <line>
                             ** <line> should be a Raw Operator, i.e. [[<line>]]
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = self.first.eval(archive)[self.times[0]].values[0]

        iterations = floor(len(archive.get_loop_iterations(line_no)) / 2)

        return Union(self.times, *[LoopIteration(self.times, line_no, i) for i in range(iterations)]).eval(archive,
                                                                                                           query_locals)


class Line(UniLateralOperator):
    """
        Line(<number>): Returns values of all objects that existed when the program hit line numbered <number>
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))

    def eval(self, archive: Optional[Archive] = None,
             query_locals: Optional[Dict[str, EvalResult]] = None) -> EvalResult:
        line_no = self.first.eval(archive)[self.times[0]].values[0]
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


class LoopIterationsTimes(UniLateralOperator, TimeOperator):
    """
        LoopIterationsTimes(<ln>): Shows the time ranges in which the iterations of the loop in line <ln> have taken place.
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))
        TimeOperator.__init__(self, times)

    def eval(self, archive: Optional[Archive] = None, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = self.first.eval(archive, query_locals)[0].values[0]

        loop_iteration_starts_and_ends: Collection[Time] = list(
            map(lambda t: t[1].time, sorted(archive.get_loop_iterations(line_no),
                                            key=lambda t: t[1].time)))

        if len(loop_iteration_starts_and_ends) % 2 != 0:
            return EvalResult.empty(self.times)

        loop_iteration_ranges = list(zip(loop_iteration_starts_and_ends[::2], loop_iteration_starts_and_ends[1::2]))

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t,
                                                       any([start <= t <= end for start, end in loop_iteration_ranges]),
                                                       [])
            for t in self.times])
