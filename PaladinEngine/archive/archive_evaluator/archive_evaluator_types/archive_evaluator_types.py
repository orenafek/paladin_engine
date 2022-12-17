from dataclasses import dataclass
from functools import reduce
from typing import *

ExpressionMapper = Mapping[str, Dict[int, object]]


class Replacement(NamedTuple):
    expression: str
    value: object
    time: int


Time = int


@dataclass
class EvalResultPair(object):
    key: str
    value: Optional[object]

    def __hash__(self):
        return hash(self.key) + hash(self.value)

    def __eq__(self, other):
        return isinstance(other, EvalResultPair) and self.key == other.key and self.value == other.value


class EvalResultEntry(dict):

    def __init__(self, time: Time, results: List[EvalResultPair], replacements: Optional[List[Replacement]]) -> None:
        self.time = time
        self.results = results
        self.replacements = replacements
        for p in results:
            self.__setattr__(p.key, p.value)

        dict.__init__(self, **{p.key: p.value for p in results})

    def create_const_copy(self, c: object):
        """
        :param c: A const value
        """
        return EvalResultEntry(self.time, [EvalResultPair(rr.key, c) for rr in self.results], self.replacements)

    @property
    def keys(self) -> Iterable[str]:
        return list({rr.key for rr in self.results})

    @property
    def values(self) -> Iterable[Optional[object]]:
        return [rr.value for rr in self.results]

    def satisfies(self) -> bool:
        return all([r.value is not None and r.value is not False for r in self.results])

    @classmethod
    def empty(cls, t: Time = -1) -> 'EvalResultEntry':
        return EvalResultEntry(t, [], [])

    @staticmethod
    def join(e1: 'EvalResultEntry', e2: 'EvalResultEntry') -> 'EvalResultEntry':
        if e1.time != e2.time:
            return EvalResultEntry.empty()

        return EvalResultEntry(e1.time, e1.results + e2.results, e1.replacements + e2.replacements)

    def __getitem__(self, key) -> Optional[EvalResultPair]:
        filtered = list(filter(lambda p: p.key == key, self.results))
        if not filtered:
            return None

        return filtered[0]

    def __getattr__(self, item):
        # TODO: fix.
        pass

    def replace_key(self, key: str, new_key: str) -> 'EvalResultEntry':
        item = self[key]
        if not item:
            raise RuntimeError(f'{key} is not a valid key.')

        self.results.remove(item)
        self.results.append(EvalResultPair(new_key, item.value))

        self.__delitem__(key)
        self.__setitem__(new_key, item.value)
        return self


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
        return list(self.satisfies_iterator())[::-1][0]

    def satisfaction_ranges(self) -> Collection[range]:
        ranges = []
        first = last = None
        for e in self.satisfies_iterator():

            if first is None:
                first = e.time
                continue

            if last is None:
                last = e.time
                continue

            if e.time - last == 1:
                last = e.time
                continue

            ranges.append(range(first, last + 1))
            first = last = None

        if first is not None and last is not None:
            ranges.append(range(first, last + 1))
        return ranges

    @staticmethod
    def _create_key(entries: Iterable[int]):
        return str((min(entries), max(entries)))

    def all_keys(self) -> Iterable[str]:
        return reduce(lambda s, keys: s.union(keys), map(lambda e: set(e.keys), self))

    def create_results_dict(self, e: EvalResultEntry) -> Dict[str, Optional[object]]:
        return {k: e[k].value if e[k] else None for k in self.all_keys()}

    def group(self) -> Dict:
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
            vals = None
            rng = []

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
        matches_time = list(filter(lambda e: e.time == t, self))
        if not matches_time:
            return EvalResultEntry.empty()

        return matches_time[0]

    @classmethod
    def empty(cls, time_range: Iterable[Time]) -> 'EvalResult':
        return EvalResult([EvalResultEntry.empty(t) for t in time_range])

    def rename_key(self, var_name: str, operator_original_name: str) -> 'EvalResult':
        for e in self:
            for k in e.keys:
                if var_name in k:
                    e.replace_key(k, k.replace(var_name, operator_original_name))
        return self

    def by_key(self, key: str) -> 'EvalResult':
        if key not in self.all_keys():
            return EvalResult.empty(range(0, len(self)))

        return EvalResult([
            EvalResultEntry(time=e.time, results=[EvalResultPair(key, e[key])], replacements=e.replacements)
            for e in self
        ])


EvalFunction = Callable[[int, int, int, int], EvalResult]
