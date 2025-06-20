"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""
import dataclasses
import re
from ast import *
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Iterable, Dict, List, Tuple, Union, Any, Type

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, ContainerId, Rk, Rv, Rvf, \
    ObjectId
from ast_common.ast_common import split_attr
from common.common import ISP, IS_ITERABLE
from module_transformer.global_map import GlobalMap


def represent(o: object):
    if any(isinstance(o, t) for t in [str, int, float, bool, complex]):
        return str(o)

    if o is None:
        return ''

    if isinstance(o, type):
        return o.__name__

    if isinstance(o, tuple):
        return (represent(x) for x in o)

    if any([isinstance(o, t) for t in {list, deque}]):
        return [represent(x) for x in o]

    if isinstance(o, set):
        return {represent(x) for x in o}

    if isinstance(o, dict):
        return {represent(k): represent(v) for (k, v) in o.items()}
    #
    # obj = {}
    # try:
    #     for attr in o.__dict__:
    #         try:
    #             obj[attr] = represent(o.__getattribute__(attr))
    #         except TypeError as e:
    #             print(e)
    # except BaseException as e:
    #     print(e)

    # return obj
    return id(o)


class Archive(object):
    GLOBAL_PALADIN_CONTAINER_ID = 1337

    class Filters(object):
        AS_OR_BMFCS_FILTER = lambda vv: vv.key.stub_name in {'__AS__', '__BMFCS__'}
        DEF_FILTER = lambda vv: vv.key.stub_name in {'__DEF__'}
        UNDEF_FILTER = lambda vv: vv.key.stub_name in {'__UNDEF__'}
        FC_FILTER = lambda vv: vv.key.stub_name in {'__FC__'}

        @classmethod
        def OR(cls, *filters):
            return lambda vv: any([f(vv) for f in filters])

        @staticmethod
        def TIME_RANGE_FILTER(time_range: range | Iterable[int]):
            return lambda vv: vv.time in time_range if time_range else lambda vv: True

        @staticmethod
        def LINE_NO_FILTER(line_no: int):
            return lambda vv: vv.line_no == line_no

        @staticmethod
        def LINE_NOS_FILTER(line_no_range: Iterable[int]):
            return lambda vv: vv.line_no in line_no_range if line_no_range else lambda vv: True

        @staticmethod
        def VALUE_FILTER(value: Any):
            return lambda vv: vv.value == value

        @staticmethod
        def REGEX_VALUE_FILTER(regex: str):
            return lambda vv: re.match(regex, str(vv.value))

        @staticmethod
        def TIME_EQUAL_OR_LATER_FILTER(time: int):
            return lambda vv: vv.time >= time

        @staticmethod
        def TIME_BEFORE_OR_EQUAL_FILTER(time: int):
            return lambda vv: vv.time <= time

        @staticmethod
        def CONTAINER_ID_EQUALS(container_id: ContainerId):
            return lambda vv: vv.key.container_id == container_id

        @staticmethod
        def FIELD_EQUALS(field: str):
            return lambda vv: vv.key.field == field

        @staticmethod
        def TIME_EQUAL_FILTER(time: Time):
            return lambda vv: vv.time == time

    class Record(object):

        class StoreKind(Enum):
            LIST_ITEM = 1, list
            SET_ITEM = 2, set
            TUPLE_ITEM = 3, tuple
            DICT_ITEM = 4, dict
            BUILTIN_MANIP = 5, object
            OBJ_ITEM = 6, object
            VAR = 7, object
            UNAMED_OBJECT = 8, object
            EVENT = 9, object
            FUNCTION_CALL = 10, object
            DEQUE_ITEM = 11, deque

            @property
            def value(self) -> int:
                return super().value[0]

            @property
            def type(self) -> Type:
                return super().value[1]

            @classmethod
            def kind_by_type(cls, t: Type) -> 'Archive.Record.StoreKind':
                if issubclass(t, list):
                    return Archive.Record.StoreKind.LIST_ITEM

                if issubclass(t, set):
                    return Archive.Record.StoreKind.SET_ITEM

                if issubclass(t, tuple):
                    return Archive.Record.StoreKind.TUPLE_ITEM

                if issubclass(t, dict):
                    return Archive.Record.StoreKind.DICT_ITEM

                if issubclass(t, deque):
                    return Archive.Record.StoreKind.DEQUE_ITEM
                return Archive.Record.StoreKind.VAR

            @classmethod
            def type_by_kind(cls, k: 'Archive.Record.StoreKind') -> Type:
                return list(filter(lambda _k: _k == k, cls))[0].type

        @dataclass
        class RecordKey(object):
            container_id: int
            field: str
            stub_name: str
            kind: 'Archive.Record.StoreKind' = dataclasses.field(default_factory=lambda: Archive.Record.StoreKind.VAR)

            def __hash__(self) -> int:
                return hash(hash(self.container_id) + hash(self.field) + hash(self.kind))

            def __eq__(self, o: object) -> bool:
                return isinstance(o, Archive.Record.RecordKey) \
                    and o.field == self.field \
                    and o.container_id == self.container_id \
                    and o.stub_name == self.stub_name \
                    and o.kind == self.kind

            def __str__(self) -> str:
                return f'{self.field}(c:{self.container_id})'

            def to_json(self):
                return self.container_id, self.field, self.stub_name, self.kind

        @dataclass
        class RecordValue(object):
            key: 'Archive.Record.RecordKey'
            rtype: type
            value: object
            expression: str
            line_no: int
            time: int = -1
            extra: str = ''

            def __str__(self) -> str:
                return f'({self.time}): {self.expression}({self.rtype.__name__}) = {self._stringify_value(self.value)} ' \
                       f'[line {self.line_no}] {f"extra: {self.extra}" if self.extra else ""}'

            def _stringify_value(self, value):
                if type(value) == list:
                    return str([self._stringify_value(i) for i in value])

                if type(value) == tuple:
                    return str((self._stringify_value(i) for i in value))

                return str(value)

            def __repr__(self):
                return self.__str__()

            def __hash__(self):
                return sum([hash(v) for v in self.__dict__.values()])

    def __init__(self) -> None:
        self.records: Dict[Archive.Record.RecordKey, List[Archive.Record.RecordValue]] = {}
        self._time: Time = -1
        self.should_record: bool = True
        self.global_map: Optional[GlobalMap] = None

    @property
    def time(self):
        self._time += 1
        return self._time

    def store(self, record_key: Record.RecordKey, record_value: Record.RecordValue, time: Time = -1):
        if not self.should_record:
            return self

        if record_key not in self.records:
            self.records[record_key] = []

        # Set time.
        if time == -1:
            record_value.time = self.time

        # Add to records.
        self.records[record_key].append(record_value)

        return self

    def retrieve(self, record_key: Record.RecordKey) -> Optional[Record]:
        return self.records[record_key]

    def reset(self):
        self.__init__()

    def to_table(self):
        try:
            header_row = list(Archive.Record.RecordKey.__dataclass_fields__) + \
                         list(Archive.Record.RecordValue.__dataclass_fields__)

            flat_records = [
                (
                    k.container_id,
                    k.field,
                    k.stub_name,
                    k.kind.name,
                    id(v.key),
                    str(v.rtype.__name__) if not isinstance(v.rtype, Tuple) else ", ".join(
                        [str(t.__name__) for t in v.rtype]),
                    represent(v.value),
                    v.expression,
                    v.line_no,
                    v.time,
                    v.extra
                )
                for k, vv in list(self.records.items()) for v in vv
            ]

            return header_row, sorted(flat_records, key=lambda r: r[len(r) - 2])

        except RuntimeError as e:
            print(e)

    def flat_and_sort_by_time(self):
        return sorted([(rk, rv) for rk in self.records for rv in self.records[rk]],
                      key=lambda r: r[1].time)

    def to_pickle(self):
        import pickle
        return pickle.dumps(self.records)

    def search_web(self, expression: str):
        raise NotImplementedError()

    @property
    def store_new(self):
        @dataclass
        class Builder_Key(object):
            _key: Archive.Record.RecordKey = None

            def key(self, container_id: int, field: str, stub_name: str,
                    kind: Archive.Record.StoreKind = Archive.Record.StoreKind.VAR):
                self._key = Archive.Record.RecordKey(container_id, field, stub_name, kind)
                return Builder(self._key)

        @dataclass
        class Builder(object):
            _key: Archive.Record.RecordKey
            _value: Archive.Record.RecordValue = None

            def value(_self, rtype: type, value: object, expression: str, line_no: int, time: int = -1,
                      extra: str = '') -> 'Archive.Record.RecordValue':
                _self._value = Archive.Record.RecordValue(_self._key, rtype, value, expression, line_no, time, extra)
                self.store(_self._key, _self._value, time)
                return _self._value

        return Builder_Key()

    def pause_record(self):
        self.should_record = False

    def resume_record(self):
        self.should_record = True

    def filter(self, filters: Union[Rvf, Iterable[Rvf]]) -> Dict[Rk, List[Rv]]:
        return {k: v for (k, v) in self.records.items() for vv in v
                if
                (IS_ITERABLE(filters) and all([f(vv) for f in filters])) or (not IS_ITERABLE(filters) and filters(vv))}

    def flatten_and_filter(self, filters: Union[Rvf, Iterable[Rvf]]) -> List[Tuple[Rk, Rv]]:
        return [(k, vv) for (k, v) in self.records.items() for vv in v
                if
                (IS_ITERABLE(filters) and all([f(vv) for f in filters])) or (not IS_ITERABLE(filters) and filters(vv))]

    def get_by_line_no(self, line_no: int) -> Dict[Rk, List[Rv]]:
        return self.filter(Archive.Filters.LINE_NO_FILTER(line_no))

    def get_loop_iterations(self, loop_line_no: int) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(
            [lambda vv: vv.key.stub_name in {'__SOLI__', '__EOLI__'},
             Archive.Filters.VALUE_FILTER(loop_line_no)])

    def get_loop_starts(self, loop_line_no: int) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(
            [lambda vv: vv.key.stub_name == '__SOL__',
             Archive.Filters.VALUE_FILTER(loop_line_no)])

    def get_by_container_id(self, container_id: int):
        return self.filter([lambda vv: vv.key.container_id == container_id, lambda vv: vv.key.stub_name == '__AS__'])

    def _all_assignments_for_object_until_time(self, object_id: int, time: int = -1):
        time_filter = (lambda t: t <= time) if time >= 0 else (lambda t: True)
        return sorted(self.flatten_and_filter([lambda vv: time_filter(vv.time),
                                               lambda vv: vv.key.container_id == object_id,
                                               lambda vv: vv.key.stub_name == '__AS__']),
                      key=lambda r: r[1].time)

    def retrieve_value(self, object_value: Union[int, object, List, Dict], object_type: type, time: int = -1):
        """
            Retrieve an object state from the archive in a certain point of time.
        :param object_value: The object to retrieve.
        :param object_type: The type of the object to retrieve.
        :param time: The time point in which the retrieved state reflected the object.
        :return:
        """
        if ISP(object_type):
            return object_value

        if object_type is list:
            return [self.retrieve_value(i, type(i), time) for i in object_value]

        if object_type is dict:
            return {self.retrieve_value(k, type(k), time): self.retrieve_value(v, type(v), time) for (k, v) in
                    object_value.items()}

        def _retrieve_object_one_level(object_id: int) -> Dict[Tuple[str, type], object]:
            return {(k.field, v.rtype): v.value for (k, v) in
                    self._all_assignments_for_object_until_time(object_id, time)}

        return {k: self.retrieve_value(v, t, time) for (k, t), v in _retrieve_object_one_level(object_value).items()}

    def object_lifetime(self, object_id: int) -> Dict[int, Union[object, Dict]]:
        """
            Retrieve the lifetime of an object.
            I.e. All values the archive has stored for that object id.
        :param object_id: The Python's Id number of the object.
        :return: A mapping between times and the values of that object in those times.
        """
        assignments = self._all_assignments_for_object_until_time(object_id)
        assignments_time = [v.time for (k, v) in assignments]
        return {t: self.retrieve_value(object_id, object, t) for t in assignments_time}

    def get_assignments(self, time_range: range = None, line_nos: Iterable[int] = None) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(
            [
                Archive.Filters.AS_OR_BMFCS_FILTER,
                Archive.Filters.TIME_RANGE_FILTER(time_range),
                Archive.Filters.LINE_NOS_FILTER(line_nos),
                lambda vv: vv.key.kind in {Archive.Record.StoreKind.VAR, Archive.Record.StoreKind.BUILTIN_MANIP, Archive.Record.StoreKind.OBJ_ITEM}
            ])

    def get_function_entries(self, func_name: str, line_no: Optional[int] = -1, entrances: bool = True,
                             in_func: bool = True, exits: bool = True, ass_and_bmfcs_only: bool = False):

        def_or_undef = Archive.Filters.OR(Archive.Filters.DEF_FILTER, Archive.Filters.UNDEF_FILTER)
        split_func_name = split_attr(func_name)
        if len(split_func_name) > 1:
            filters = [Archive.Filters.VALUE_FILTER(func_name)]
        else:
            filters = [Archive.Filters.REGEX_VALUE_FILTER(r"(?:\b\w+\.)?" + re.escape(func_name) + r"\b")]

        if line_no is not None and line_no > 0:
            filters.append(Archive.Filters.LINE_NO_FILTER(line_no))

        if not in_func:
            if entrances and not exits:
                filters.append(Archive.Filters.DEF_FILTER)

            if not entrances and exits:
                filters.append(Archive.Filters.UNDEF_FILTER)

            if entrances and exits:
                filters.append(def_or_undef)

            return self.flatten_and_filter(filters)

        # in_func == True
        filters.append(def_or_undef)
        function_entrances_and_exits = sorted(self.flatten_and_filter(filters), key=lambda r: r[1].time)
        if len(function_entrances_and_exits) % 2 == 1:
            # noinspection PyTypeChecker
            function_entrances_and_exits.append(None)

        entries = function_entrances_and_exits
        for func_entrance, func_exit in zip(function_entrances_and_exits[::2], function_entrances_and_exits[1::2]):
            filters = [self.Filters.LINE_NOS_FILTER(range(*self.global_map.functions[func_entrance[1].value]))] + \
                      [Archive.Filters.AS_OR_BMFCS_FILTER] if ass_and_bmfcs_only else []
            if func_exit is not None:
                filters.append(self.Filters.TIME_RANGE_FILTER(range(func_entrance[1].time + 1, func_exit[1].time)))
            else:
                filters.append(self.Filters.TIME_EQUAL_OR_LATER_FILTER(func_entrance[1].time))

            entries.extend(self.flatten_and_filter(filters))

        entries = list(filter(lambda e: e is not None, entries))
        if not entrances:
            entries = filter(lambda r: r[0].stub_name != '__DEF__', entries)

        if not exits:
            entries = filter(lambda r: r[0].stub_name != '__UNDEF__', entries)

        return sorted(entries, key=lambda r: r[1].time)

    def find_events(self, line_no: int = -1, time_range: Iterable[int] = None) -> List[Tuple[Rk, Rv]]:
        filters = [lambda vv: vv.key.stub_name not in {'__SOLI__', '__EOLI__'}]
        if line_no > -1:
            filters.append(Archive.Filters.LINE_NO_FILTER(line_no))

        if time_range is not None:
            filters.append(Archive.Filters.TIME_RANGE_FILTER(time_range))

        return self.flatten_and_filter(filters)

    def get_print_events(self, output: str) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(lambda vv: vv.key.stub_name == '__PRINT__' and vv.value == output)

    @property
    def last_time(self) -> int:
        return self._time

    def flatten(self) -> Iterable[Tuple[Rk, Rv]]:
        return [(rk, vv) for rk, rv in self.records.items() for vv in rv]

    def get_line_nos_for_time(self, time: int) -> Iterable[int]:
        return {rv.line_no for _, rv in self.flatten() if rv.time == time}

    def get_function_line_nos(self, func_name: str) -> Tuple[int, int]:
        func_entries = self.get_function_entries(func_name)
        func_defs = map(lambda t: t[1].line_no, filter(lambda t: Archive.Filters.DEF_FILTER(t[1]), func_entries))
        func_start_line_no = list(func_defs)[0]
        assert all([func_def == func_start_line_no for func_def in func_defs])

        func_undefs = map(lambda t: t[1].line_no, filter(lambda t: Archive.Filters.UNDEF_FILTER(t[1]), func_entries))
        func_end_line_no = max(func_undefs)

        return func_end_line_no, func_end_line_no

    def get_call_chain(self, include_builtin=True) -> Dict[Time, Tuple[str, str]]:
        out_format = lambda rv: (rv.extra, rv.expression)
        if include_builtin:
            return {rv.time: out_format(rv) for rk, rv in
                    sorted(self.flatten_and_filter(self.Filters.FC_FILTER), key=lambda t: t[1].time)}

        records = sorted(
            self.flatten_and_filter(self.Filters.OR(self.Filters.FC_FILTER, self.Filters.DEF_FILTER)),
            key=lambda t: t[1].time)

        if len(records) == 0:
            return {}

        if len(records) == 1:
            return {rv.time: out_format(rv) for rk, rv in records}

        def records_match(rv1: Archive.Record.RecordValue, rv2: Archive.Record.RecordValue):
            """
            Should be looking for same function name in FC and DEF, but some functions are not stored the same.
            E.g.: Constructors: for A(), the __FC__ is for "A" and the __DEF__ is for "A.__init__"
            """
            if not (rv1.key.stub_name == '__FC__' and rv2.key.stub_name == '__DEF__'):
                return False

            if rv1.expression == rv2.expression:
                return True

            # Deal with constructors.
            if f'{rv1.expression}.__init__' == rv2.expression:
                return True

            return False

        local_func_records = [records[i] for i in range(len(records) - 1) if
                              records_match(records[i][1], records[i + 1][1])]
        return {rv.time: (rv.extra, rv.expression) for rk, rv in local_func_records}

    def exists(self, value: ObjectId):
        return len(self.filter(Archive.Filters.VALUE_FILTER(value))) > 0
