import math
import os
import re
from asyncio import as_completed
from collections import OrderedDict
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import reduce
from typing import *
from typing import Callable

import frozendict

from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import SCOPE_SIGN
from common.attributed_dict import AttributedDict
from utils.range_dict import RangeDict

ExpressionMapper = Mapping[str, Dict[int, object]]


class Replacement(NamedTuple):
    expression: str
    value: object
    time: int


Time = int
ObjectId = int
LineNo = int
ContainerId = int

Identifier: Type = Union[str, ObjectId]
ParseResults: Type = Dict[str, Dict[str, Any]]

BUILTIN_CONSTANTS_STRINGS = ['inf', '-inf', 'nan']
BUILTIN_SPECIAL_FLOATS = {c: float(c) for c in BUILTIN_CONSTANTS_STRINGS}
EVAL_BUILTIN_CLOSURE = {**BUILTIN_SPECIAL_FLOATS, frozendict.__name__: frozendict, deque.__name__: deque,
                        list.__name__: list, AttributedDict.__name__: AttributedDict}
BAD_JSON_VALUES = {'-Infinity': '"-∞"', 'Infinity': '"∞"', 'NaN': '"NaN"'}


@dataclass
class Scope(object):
    line_no: LineNo
    data: Dict[ContainerId, RangeDict] = field(default_factory=lambda: {})

    def add_data(self, container_id: ContainerId, data: RangeDict):
        self.data[container_id] = data
        return data

    def __hash__(self) -> int:
        return hash(self.line_no)

    def __getitem__(self, item):
        if not isinstance(item, ContainerId):
            return None

        return self.data[item] if item in self.data else None

    def __contains__(self, item):
        return item in self.data

    def get_data_by_time(self, time: Time):
        proximity_list = filter(lambda i: i[0] is not None,
                                [(rd.get_closest(time)[1], rd) for rd in self.data.values()])
        min_diff = math.inf
        closest = None
        for t, data in proximity_list:
            diff = abs(t - time)
            if diff < min_diff:
                closest = data
                min_diff = diff

        if closest is None:
            return None

        return closest
        # for rd in self.data.values():
        #     closest_value, closest_time = rd.get_closest(time)
        #     if closest_time is not None:
        #         return rd
        # for min_time, max_time in sorted(self.time_mapping.keys()):
        #     if min_time <= time <= max_time:
        #         return self.data[self.time_mapping[(min_time, max_time)]]
        # else:
        #     return None

    @property
    def container_ids(self) -> List[ContainerId]:
        return list(self.data.keys())


@dataclass
class EvalResultPair(object):
    key: str
    value: Optional[object]

    def __hash__(self):
        return hash(self.key) + hash(self.value)

    def __eq__(self, other):
        return isinstance(other, EvalResultPair) and self.key == other.key and self.value == other.value


class EvalResultEntry(OrderedDict):

    def __init__(self, time: Time, results: List[EvalResultPair],
                 replacements: Optional[List[Replacement]] = None) -> None:
        self.time = time
        self.evaled_results = results
        self.replacements = replacements
        attributes = self.populate(results)

        dict.__init__(self, **attributes)

    def populate(self, results):
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

        return attributes

    def create_const_copy(self, c: object):
        """
        :param c: A const value
        """
        return EvalResultEntry(self.time, [EvalResultPair(rr.key, c) for rr in self.evaled_results], self.replacements)

    @classmethod
    def create_const(cls, t: Time, k: str, c: object):
        return EvalResultEntry(t, [EvalResultPair(k, c)], [])

    @property
    def keys(self) -> List[str]:
        return list(dict.fromkeys(map(lambda rr: rr.key, self.evaled_results)))

    @property
    def values(self) -> List[Optional[object]]:
        return [rr.value for rr in self.evaled_results]

    @property
    def items(self) -> List[Tuple[Any, Any]]:
        return [(rr.key, rr.value) for rr in self.evaled_results]

    @property
    def items_no_scope_signs(self) -> 'AttributedDict':
        return AttributedDict([(re.sub(r'\b(.+?)@\d+\b', r'\1', rr[0]), rr[1]) for rr in self.items])

    def satisfies(self) -> bool:
        return all([r.value is not None and r.value is not False and r.value != [None] for r in self.evaled_results])

    def extend_with_empty_keys(self, keys: Iterable[str]):
        return EvalResultEntry(self.time, EvalResultEntry.join_evaled_results(self,
                                                                              EvalResultEntry.empty_with_keys(self.time,
                                                                                                              keys)))

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

        return EvalResultEntry(e1.time, EvalResultEntry.join_evaled_results(e1, e2), [])

    @staticmethod
    def join_evaled_results(e1: 'EvalResultEntry', e2: 'EvalResultEntry') -> List[EvalResultPair]:

        res = []
        all_keys = OrderedDict.fromkeys([*e1.keys, *e2.keys])

        # Add keys only from e1.
        res.extend([e1[k] for k in all_keys.keys() if k not in e2.keys])

        # Add keys only from e2.
        res.extend([e2[k] for k in all_keys.keys() if k not in e1.keys])

        # Add values from mutual keys.
        for k in filter(lambda k: k in e1.keys and k in e2.keys, all_keys.keys()):
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
        return repr(self.items)


class EvalResult(List[EvalResultEntry]):

    def __init__(self, seq=()):
        super().__init__(seq)
        self._last_hash = -1
        self._all_keys = []

    def __hash__(self) -> int:
        return hash(sum([hash(x for x in self)]))

    @classmethod
    def create_const_copy(cls, r: 'EvalResult', c: object):
        return EvalResult([EvalResultEntry.create_const_copy(e, c) for e in r])

    @classmethod
    def create_const(cls, times: Iterable[Time], k: str, c: object):
        return EvalResult([EvalResultEntry.create_const(t, k, c) for t in times])

    def all_satisfies(self):
        return all([e.satisfies() for e in self])

    def satisfies_iterator(self) -> Iterator['EvalResultEntry']:
        return filter(lambda e: e.satisfies(), self)

    def first_satisfaction(self) -> EvalResultEntry:
        try:
            return next(self.satisfies_iterator())
        except StopIteration:
            return EvalResultEntry.empty(-1)

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
        if hash(self) == self._last_hash:
            return self._all_keys

        self._last_hash = hash(self)
        self._all_keys = reduce(lambda acc, new_keys: OrderedDict.fromkeys([*acc.keys(), *new_keys]),
                                map(lambda e: list(OrderedDict.fromkeys(e.keys)), self), OrderedDict()).keys()
        return self._all_keys

    def create_results_dict(self, e: EvalResultEntry) -> Dict[str, Optional[object]]:
        return {k: e[k].value if e[k] else None for k in self.all_keys()}

    def group(self) -> ParseResults:
        if len(self) == 0:
            return {}

        res = {}

        rng = []
        vals = None
        for e in sorted(self, key=lambda e: e.time):
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

        # Filter out empty results.
        res = {k: v for k, v in res.items() if not all([vv is None for vv in v.values()])}
        return res

    def is_empty(self):
        return len(self) == 0

    def times(self):
        return sorted([e.time for e in self])


    @classmethod
    def join(cls, r1: 'EvalResult', r2: 'EvalResult'):

        if not r1:
            return r2

        if not r2:
            return r1

        results = []
        r1_times = r1.times()
        r2_times = r2.times()

        r1_time_mapped: Dict[Time, EvalResultEntry] = {e.time: e for e in r1}
        r2_time_mapped: Dict[Time, EvalResultEntry] = {e.time: e for e in r2}

        r1_keys = r1.all_keys()
        r2_keys = r2.all_keys()

        for t in range(min(r1_times + r2_times), max(r1_times + r2_times) + 1):
            if t not in r1_time_mapped and t not in r2_time_mapped:
                continue
            elif t in r1_time_mapped and t in r2_time_mapped:
                results.append(EvalResultEntry.join(r1_time_mapped[t], r2_time_mapped[t]))
            elif t not in r2_time_mapped:
                results.append(r1_time_mapped[t].extend_with_empty_keys(r2_keys))
            elif t not in r1_time_mapped:
                results.append(r2_time_mapped[t].extend_with_empty_keys(r1_keys))

        return EvalResult(results)

    def __add__(self, other: 'EvalResult') -> 'EvalResult':
        return EvalResult.join(self, other)

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

    def rename_key(self, new: str, old: str):
        for e in self:
            for k in e.keys:
                if old in k:
                    e.replace_key(k, k.replace(old, new))

        self._last_hash = -1

    def by_key(self, key: str) -> 'EvalResult':
        if key not in self.all_keys():
            return EvalResult.empty(range(0, len(self)))

        return EvalResult([
            EvalResultEntry(time=e.time, results=[EvalResultPair(key, e[key])], replacements=e.replacements)
            for e in self
        ])


EvalFunction = Callable[[int, int, int, int], EvalResult]
SemanticsArgType = Union[bool, EvalResult]

Rk = 'Archive.Record.RecordKey'
Rv = 'Archive.Record.RecordValue'
Rvf = Callable[['Archive.Record.RecordValue'], bool]
