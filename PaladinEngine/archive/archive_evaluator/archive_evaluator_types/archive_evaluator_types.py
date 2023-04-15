from dataclasses import dataclass
from functools import reduce
from typing import *

import frozendict

from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import SCOPE_SIGN

ExpressionMapper = Mapping[str, Dict[int, object]]


class Replacement(NamedTuple):
    expression: str
    value: object
    time: int


Time = int
ObjectId = int
LineNo = int
ContainerId = int
Scope = Tuple[LineNo, ContainerId]

Identifier: Type = Union[str, ObjectId]
ParseResults: Type = Dict[str, Dict[str, Any]]

BUILTIN_CONSTANTS_STRINGS = ['inf', '-inf', 'nan']
BUILTIN_SPECIAL_FLOATS = {c: float(c) for c in BUILTIN_CONSTANTS_STRINGS}
EVAL_BUILTIN_CLOSURE = {**BUILTIN_SPECIAL_FLOATS, frozendict.__name__: frozendict}
BAD_JSON_VALUES = {'Infinity': '"∞"', 'NaN': '"NaN"'}


@dataclass
class EvalResultPair(object):
    key: str
    value: Optional[object]

    def __hash__(self):
        return hash(self.key) + hash(self.value)

    def __eq__(self, other):
        return isinstance(other, EvalResultPair) and self.key == other.key and self.value == other.value


class EvalResultEntry(dict):

    def __init__(self, time: Time, results: List[EvalResultPair],
                 replacements: Optional[List[Replacement]] = None) -> None:
        self.time = time
        self.evaled_results = results
        self.replacements = replacements
        attributes = {}
        for p in results:
            if SCOPE_SIGN in p.key:
                var_without_scope, scope = p.key.split(SCOPE_SIGN, maxsplit=1)
                attributes[var_without_scope + "_" + scope] = p.value
                attributes[var_without_scope] = p.value
            else:
                attributes[p.key] = p.value

        for attr_k, attr_v in attributes.items():
            self.__setattr__(attr_k, attr_v)

        dict.__init__(self, **attributes)

    def create_const_copy(self, c: object):
        """
        :param c: A const value
        """
        return EvalResultEntry(self.time, [EvalResultPair(rr.key, c) for rr in self.evaled_results], self.replacements)

    @property
    def keys(self) -> Iterable[str]:
        return list({rr.key for rr in self.evaled_results})

    @property
    def values(self) -> Iterable[Optional[object]]:
        return [rr.value for rr in self.evaled_results]

    def satisfies(self) -> bool:
        return all([r.value is not None and r.value is not False and r.value != [None] for r in self.evaled_results])

    @classmethod
    def empty(cls, t: Time = -1) -> 'EvalResultEntry':
        return EvalResultEntry(t, [], [])

    @classmethod
    def empty_with_keys(cls, t: Time = -1, keys: Optional[Iterable[str]] = None):
        return EvalResultEntry(t, [EvalResultPair(k, None) for k in keys], [])

    @staticmethod
    def join(e1: 'EvalResultEntry', e2: 'EvalResultEntry') -> 'EvalResultEntry':
        if e1 and not e2:
            return e1

        if not e1 and e2:
            return e2

        if e1.time != e2.time:
            return EvalResultEntry.empty()

        return EvalResultEntry(e1.time, EvalResultEntry.__join_evalued_results(e1, e2),
                               e1.replacements + e2.replacements)

    @staticmethod
    def __join_evalued_results(e1: 'EvalResultEntry', e2: 'EvalResultEntry') -> List[EvalResultPair]:

        res = []
        all_keys = {*e1.keys, *e2.keys}

        # Add keys only from e1.
        res.extend([e1[k] for k in all_keys.difference({*e2.keys})])

        # Add keys only from e2.
        res.extend([e2[k] for k in all_keys.difference({*e1.keys})])

        # Add values from mutual keys.
        pair = None
        for k in {*e1.keys}.intersection({*e2.keys}):
            if e1[k].value is e2[k].value is None:
                pair = e1[k]
            elif e1[k].value is not None and e2[k].value is None:
                pair = e1[k]
            elif e1[k].value is None and e2[k].value is not None:
                pair = e2[k]
            else:
                # TODO: What should be done here? For now, choose e1 randomly...
                pair = e1[k]

            res.append(pair)

        return res

    def __getitem__(self, key) -> Optional[EvalResultPair]:
        filtered = list(filter(lambda p: p.key == key, self.evaled_results))
        if not filtered:
            return None

        return filtered[0]

    def replace_key(self, key: str, new_key: str) -> 'EvalResultEntry':
        item = self[key]
        if not item:
            raise RuntimeError(f'{key} is not a valid key.')

        self.evaled_results.remove(item)
        self.evaled_results.append(EvalResultPair(new_key, item.value))

        del self[key]
        self[new_key] = item.value

        delattr(self, key)
        setattr(self, new_key, item.value)
        return self

    def __iter__(self) -> Iterator[EvalResultPair]:
        return super().__iter__()

    def __repr__(self):
        return super().__repr__() + ' {' + str(self.time) + '}'


class EvalResult(List[EvalResultEntry]):
    EMPTY = []

    @classmethod
    def create_const_copy(cls, r: 'EvalResult', c: object):
        return [EvalResultEntry.create_const_copy(e, c) for e in r]

    def all_satisfies(self):
        return all([e.satisfies() for e in self])

    def satisfies_iterator(self) -> Iterator['EvalResultEntry']:
        return filter(lambda e: e.satisfies(), self)

    def first_satisfaction(self) -> EvalResultEntry:
        return next(self.satisfies_iterator())

    def last_satisfaction(self) -> EvalResultEntry:
        it = list(self.satisfies_iterator())
        if not it:
            return EvalResultEntry.empty()
        return it[::-1][0]

    def satisfaction_ranges(self, all_times: Iterable[Time]) -> Collection[range]:
        def create_range(times: List[Time]) -> range:
            return range(times[::-1][0], times[0] + 1)

        ranges = []
        satisfaction_times = self.satisfaction_times()
        rng = []
        for t, res in [(t, t in satisfaction_times) for t in all_times]:
            if not rng and not res:
                continue

            elif not rng and res:
                rng = [t]

            elif res and t == rng[0] + 1:
                # Extend range.
                rng.insert(0, t)

            elif res and t != rng[0] + 1:
                # The range should be completed, start a new range with t
                ranges.append(create_range(rng))
                rng = [t]

            else:  # not res and rng != [].
                # The last range should be completed.
                ranges.append(create_range(rng))
                rng = []

        if rng:
            ranges.append(create_range(rng))
        return ranges

    def satisfaction_times(self) -> Iterable[Time]:
        return list(map(lambda e: e.time, self.satisfies_iterator()))

    @staticmethod
    def _create_key(entries: Iterable[int]):
        return str((min(entries), max(entries)))

    def all_keys(self) -> Iterable[str]:
        return reduce(lambda s, keys: s.union(keys), map(lambda e: set(e.keys), self), set())

    def create_results_dict(self, e: EvalResultEntry) -> Dict[str, Optional[object]]:
        return {k: e[k].value if e[k] else None for k in self.all_keys()}

    def group(self) -> ParseResults:
        if len(self) == 0:
            return {}

        res = {}

        rng = []
        vals = None
        for e in self:
            if not vals:
                # New range.
                vals = self.create_results_dict(e)
                rng.append(e.time)
                continue

            new_vals = self.create_results_dict(e)

            # If the same as the value before, extend the range.
            if new_vals == vals:
                rng.append(e.time)
                continue

            # Otherwise, the range is complete, add it to res.
            res[EvalResult._create_key(rng)] = vals
            vals = new_vals
            rng = [e.time]

        # Add last range if such exist.
        if rng and vals:
            res[EvalResult._create_key(rng)] = vals

        return res

    @classmethod
    def join(cls, r1: 'EvalResult', r2: 'EvalResult'):

        if not r1:
            return r2

        if not r2:
            return r1

        results = []
        r1_time_mapped = {e.time: e for e in r1}
        r2_time_mapped = {e.time: e for e in r2}

        for t in set(r1_time_mapped).union(r2_time_mapped):
            if t in r1_time_mapped and t not in r2_time_mapped:
                results.append(r1_time_mapped[t])

            elif t not in r1_time_mapped and t in r2_time_mapped:
                results.append(r2_time_mapped[t])

            else:
                results.append(EvalResultEntry.join(r1_time_mapped[t], r2_time_mapped[t]))

        return EvalResult(results)

    def __getitem__(self, t: Time):
        matches_time = list(filter(lambda e: e and e.time == t, self))
        if not matches_time:
            return EvalResultEntry.empty_with_keys(t, self.all_keys())

        return matches_time[0]

    def __repr__(self):
        return [_ for _ in self].__repr__()

    @classmethod
    def empty(cls, time_range: Iterable[Time]) -> 'EvalResult':
        return EvalResult([EvalResultEntry.empty(t) for t in time_range])

    @staticmethod
    def rename_key(result: 'EvalResult', operator_original_name: str, var_name: str) -> 'EvalResult':
        for e in result:
            for k in e.keys:
                if var_name in k:
                    e.replace_key(k, k.replace(var_name, operator_original_name))

        return result

    def by_key(self, key: str) -> 'EvalResult':
        if key not in self.all_keys():
            return EvalResult.empty(range(0, len(self)))

        return EvalResult([
            EvalResultEntry(time=e.time, results=[EvalResultPair(key, e[key])], replacements=e.replacements)
            for e in self
        ])


EvalFunction = Callable[[int, int, int, int], EvalResult]
SemanticsArgType = Union[bool, EvalResult]
