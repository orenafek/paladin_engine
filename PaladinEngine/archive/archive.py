"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""
import dataclasses
import json
import traceback
from ast import *
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Iterable, Dict, List, Tuple, Union, Any, Callable, Type

import pandas as pd
from frozendict import frozendict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time
from ast_common.ast_common import ast2str
from builtin_manipulation_calls.builtin_manipulation_calls import __BUILTIN_COLLECTIONS_MANIPULATION_METHODS__, \
    __BUILTIN_COLLECTIONS__
from common.common import ISP, IS_ITERABLE

Rk = 'Archive.Record.RecordKey'
Rv = 'Archive.Record.RecordValue'
Rvf = Callable[['Archive.Record.RecordValue'], bool]


def represent(o: object):
    if any(isinstance(o, t) for t in [str, int, float, bool, complex]):
        return str(o)

    if o is None:
        return ''

    if isinstance(o, type):
        return o.__name__

    if isinstance(o, tuple):
        return (represent(x) for x in o)

    if isinstance(o, list):
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

    def __init__(self) -> None:
        self.records: Dict[Archive.Record.RecordKey, List[Archive.Record.RecordValue]] = {}
        self._time = -1
        self.should_record = True
        self.object_builder = Archive.ObjectBuilder(self)

    @property
    def time(self):
        self._time += 1
        return self._time

    def store(self, record_key: Record.RecordKey, record_value: Record.RecordValue):
        if not self.should_record:
            return self

        if record_key not in self.records:
            self.records[record_key] = []

        # Set time.
        record_value.time = self.time

        # Add to records.
        self.records[record_key].append(record_value)

        return self

    def retrieve(self, record_key: Record.RecordKey) -> Optional[Record]:
        return self.records[record_key]

    def reset(self):
        self.records.clear()

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
                    str(v.rtype.__name__),
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

    def __repr__(self):
        header, rows = self.to_table()
        data_frame = pd.DataFrame(columns=header, data=rows)
        return data_frame.to_markdown(index=True)

    def build_object(self, object_id: int, rtype: type = Any, time: int = -1) -> Any:
        return self.object_builder.build(object_id, rtype, time)

    class ObjectBuilder(object):
        SUPPOERTED_BUILTIN_COLLECTION_TYPES = {*__BUILTIN_COLLECTIONS__, tuple}

        def __init__(self, archive: 'Archive'):
            self.archive = archive
            self.built_objects = {}
            self.used_records = []

        @staticmethod
        def time_filter(rv: 'Archive.Record.RecordValue', time: Time):
            return rv.time <= time if time != -1 else True

        def get_relevant_records(self, object_id: int, time: int) -> List[Tuple[Rk, Rv]]:
            return sorted(self.archive.flatten_and_filter([lambda vv: vv.key.container_id == object_id,
                                                           lambda vv: vv.key.stub_name in {'__AS__', '__BMFCS__'},
                                                           lambda vv: Archive.ObjectBuilder.time_filter(vv, time),
                                                           #lambda vv: vv not in self.used_records
                                                           ]), key=lambda t: t[1].time)

        def build(self, object_id: int, rtype: type = Any, time: int = -1) -> Any:
            try:
                # Extract from built objects' cache.
                obj = self.built_objects[object_id] if object_id in self.built_objects else None

                relevant_records = self.get_relevant_records(object_id, time)

                if not relevant_records:
                    # The object is already built and there are no relevant records to update its value.
                    if obj is not None:
                        return obj

                    # The object is not already built and no relevant records.
                    if rtype in Archive.ObjectBuilder.SUPPOERTED_BUILTIN_COLLECTION_TYPES:
                        # The object should be an empty builtin collection
                        return rtype()

                    # Otherwise, no object has been built and no relevant records to update it.
                    return None

                while relevant_records:
                    k, v = relevant_records.pop()
                    value = v.value if ISP(v.rtype) else self.build(v.value, v.rtype, time)
                    self.used_records.append(v)

                    obj = Archive.ObjectBuilder.update_object_by_kind(k, obj, rtype, value)

                    relevant_records = self.get_relevant_records(object_id, time)

                if isinstance(obj, dict):
                    obj = frozendict(obj)

                self.built_objects[object_id] = obj
                return obj

            except (TypeError, IndexError):
                traceback.print_exc()
                return None

        @staticmethod
        def update_object_by_kind(k, obj, rtype, value):
            if k.kind == Archive.Record.StoreKind.BUILTIN_MANIP:
                if not obj:
                    obj = rtype()
                obj.__getattribute__(k.field)(value)

            elif k.kind in {Archive.Record.StoreKind.VAR, Archive.Record.StoreKind.DICT_ITEM}:
                if not obj:
                    obj = {}

                if isinstance(obj, frozendict):
                    obj = dict(obj)

                obj[k.field] = value

            elif k.kind == Archive.Record.StoreKind.LIST_ITEM:
                if not obj:
                    obj = []
                if k.field < len(obj):
                    obj[k.field] = value
                else:
                    obj.insert(k.field, value)

            elif k.kind == Archive.Record.StoreKind.SET_ITEM:
                if not obj:
                    obj = set()
                obj.add(value)

            elif k.kind == Archive.Record.StoreKind.TUPLE_ITEM:
                obj = (*obj, value) if obj else (value,)
            return obj

    def search_web(self, expression: str):
        def search_web_inner(container_id, field):
            for key in self.records:
                if key.field == field and (not container_id or key.container_id == container_id):
                    return self.records[key][0]

        container_id = None
        for element in expression.split('.'):
            record_value: Archive.Record.RecordValue = search_web_inner(container_id, element)
            if not record_value:
                return ''

            if record_value.rtype in [str, int, float, bool, complex]:
                return str(record_value.value)

            container_id = record_value.value if type(record_value.value) is int else id(record_value.value)

        # Getting here means that the last record value found is of an object and not primitive.
        # assert record_value and record_value.rtype is not int and type(record_value.value) is int
        return json.dumps(self.build_object(record_value.value))

    def search(self, expression: str, frame: dict = None) -> Optional[Iterable[Record.RecordValue]]:
        for key in self.records.keys():
            if key.field == expression:
                return self.records[key]
            record_values = [rv for rv in self.records[key] if rv.expression == expression]
            if record_values:
                return record_values

        return None

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
                self.store(_self._key, _self._value)
                return _self._value

        return Builder_Key()

    def __str__(self):
        return self.__repr__()

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
        return self.filter(lambda vv: vv.line_no == line_no)

    def get_assignments_by_line_no(self, line_no: int) -> Dict[Rk, List[Rv]]:
        return self.filter([lambda vv: vv.line_no == line_no, lambda vv: vv.key.stub_name == '__AS__'])

    def get_loop_iterations(self, loop_line_no: int) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(
            lambda vv: vv.key.stub_name in {'__SOLI__', '__EOLI__'} and vv.value == loop_line_no)

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

    def get_assignments(self, time_range: range = None, line_no_range: range = None) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(
            [
                lambda vv: vv.key.stub_name in {'__AS__', '__BMFCS__'},
                lambda vv: vv.time in time_range if time_range else lambda vv: True,
                lambda vv: vv.line_no in line_no_range if line_no_range else lambda vv: True,
                lambda vv: vv.key.kind in {Archive.Record.StoreKind.VAR, Archive.Record.StoreKind.BUILTIN_MANIP}
            ])

    def get_scope_by_line_no(self, line_no: int) -> int:
        """
            Returns the "scope", meaning the container_id (id of the frame) of variables (not object's fields) that are referenced in a line_no.
        :param line_no: The line no.
        :return: scope.
        """
        # Get all records by time.
        record_values_by_time = [rv for _, rv in self.flat_and_sort_by_time()]

        rv_stack = []
        for rv in record_values_by_time:
            if rv.key.stub_name == '__DEF__':
                rv_stack.append(rv)
                continue

            if rv.key.stub_name == '__UNDEF__':
                rv_stack.pop()
                continue

            if rv.line_no == line_no:
                if len(rv_stack) > 0:
                    return rv_stack[-1].key.container_id
                else:
                    return rv.key.container_id
                # TODO: Should we continue or raise an error? This case should happen when the line_no comes before
                #  no __DEF__.

        # TODO: Raise an error?
        return -1

    def find_by_line_no(self, expression: str, line_no: int, time: int = -1) -> Dict[int, List[Rv]]:
        """
        Find the values of an expression in the archive throughout its time, where the names are bounded to a scope
        of a line no.
        @param expression: The expression to look for.
        @param line_no: The line no to bound a scope for.
        @param time:
        @return:
        """
        scope = self.get_scope_by_line_no(line_no) if line_no != -1 else -1
        archive = self

        def _find_by_name_and_container_id(name: str, container_id: int) -> List['Archive.Record.RecordValue']:
            return [r[1] for r in self.flatten_and_filter(
                lambda
                    vv: vv.key.container_id == container_id and vv.key.field == name and vv.time <= time)]

        def _find_by_name(name: str) -> List['Archive.Record.RecordValue']:
            return [r[1] for r in self.flatten_and_filter(lambda vv: vv.key.field == name and vv.time <= time)]

        @dataclass
        class NodeFinder(NodeVisitor):
            def __init__(self, archive: 'Archive'):
                self.archive = archive
                self.values = {}

            def visit_Subscript(self, node: Subscript) -> Any:
                # TODO: Handle.
                raise NotImplementedError('TODO: Fix.')

            def visit_Attribute(self, node: Attribute) -> Any:
                # Resolve value (lhs of "lhs.rhs").
                self.visit(node.value)
                value_str = ast2str(node.value)
                attr_str = ast2str(node)
                self.values[attr_str] = {}

                if value_str not in self.values:
                    return None

                # Add attribute's value.
                for t, v in self.values[value_str].items():
                    if type(v) is int:
                        # v is probably an object id.
                        obj = archive.build_object(v, time=time)
                        if obj == []:
                            # TODO: I don't know what to do here...
                            continue
                        if len(obj) > 1:
                            # TODO: Or here...
                            pass
                        attr = obj[0][node.attr]
                    else:
                        attr = v.__getattribute__(node.attr)

                    self.values[attr_str][t] = attr

            def visit_Name(self, node: Name) -> Any:
                self.values[node.id] = {
                    rv.time:
                        rv.value if ISP(rv.rtype) else archive.build_object(rv.value, rv.rtype, time)
                    for rv in
                    (_find_by_name_and_container_id(node.id, scope) if scope != -1 else _find_by_name(node.id))
                }

            def visit(self, node: AST) -> 'NodeFinder':
                super(NodeFinder, self).visit(node)
                return self

        return NodeFinder(self).visit(parse(expression).body[0]).values

    def find_events(self, line_no: int) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(lambda vv: vv.line_no == line_no)

    def get_print_events(self, output: str) -> List[Tuple[Rk, Rv]]:
        return self.flatten_and_filter(lambda vv: vv.key.stub_name == '__PRINT__' and vv.value == output)

    @property
    def last_time(self) -> int:
        return self._time

    def flatten(self) -> Iterable[Tuple[Rk, Rv]]:
        return [(rk, vv) for rk, rv in self.records.items() for vv in rv]
