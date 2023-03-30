import copy
from dataclasses import dataclass
from functools import reduce
from types import NoneType
from typing import *

from ranges import Range, RangeDict

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, ObjectId, LineNo
from archive.object_builder.object_builder import ObjectBuilder
from builtin_manipulation_calls.builtin_manipulation_calls import BuiltinCollectionsUtils, Postpone, EMPTY, \
    EMPTY_COLLECTION
from common.common import ISP
from stubs.stubs import __AS__, __BMFCS__, __FC__

_NAMED_PRIMITIVES_DATA_TYPE = Dict[str, Dict[LineNo, Tuple[Type, RangeDict]]]
_NAMED_OBJECTS_DATA_TYPE = Dict[str, Dict[LineNo, RangeDict]]


class DiffObjectBuilder(ObjectBuilder):
    ObjectEntry = Tuple[Type, Any]

    @dataclass
    class _FunctionCallFieldType(object):
        _type: Type

        def __eq__(self, other):
            return isinstance(other, DiffObjectBuilder._FunctionCallFieldType) and self._type == other._type or \
                   isinstance(other, type) and other == self._type

        def __hash__(self):
            return hash(self._type)

    class AttributedDict(Dict):
        def __hash__(self) -> int:
            return hash(str(self))

    @dataclass
    class _DictKeyResolve(object):
        field_type: Type
        field: Union[str, Any, ObjectId]
        value_type: Type
        value: Any

        def __hash__(self) -> int:
            return hash(hash(self.field_type) + hash(self.field) + hash(self.value_type) + hash(self.value))

    def __init__(self, archive: Archive):
        ObjectBuilder.__init__(self, archive)
        self.archive = archive
        self._data: Dict[ObjectId, RangeDict] = {}
        self._last_range: Dict[ObjectId, Range] = {}
        self._built_objects: Dict[Tuple[ObjectId, Time], Any] = {}
        self._named_primitives: _NAMED_PRIMITIVES_DATA_TYPE = {}
        self._named_objects: _NAMED_OBJECTS_DATA_TYPE = {}
        self._construct()

    def build(self, item: Union[str, ObjectId], time: Time, _type: Type = Any, line_no: Optional[LineNo] = -1) -> Any:
        if isinstance(item, str):
            object_type, object_id, obj_data = self._get_data_from_named(item, time, line_no)
            if ISP(object_type) or object_type is NoneType:
                return obj_data
        else:
            # If the object asked to be built is a primitive, or it's not an object in the data
            if ISP(_type) or item not in self._data:
                return item

            object_type, object_id, obj_data = _type, item, self._data[item]

        # If the object has been already built for time, return it.
        if (object_id, time) in self._built_objects:
            return self._built_objects[object_id, time]

        object_data = self.__get_latest_object_data(object_id, time, object_type)
        if not object_data:
            return None

        # Build object and store if for future references.
        built_object = self._built_objects[(object_id, time)] = self._build_object(line_no, object_data, object_type,
                                                                                   time)
        return built_object

    def _build_object(self, line_no: LineNo, object_data: RangeDict, object_type: Type, time: Time):
        evaluated_object = DiffObjectBuilder.AttributedDict()
        to_evaluate = list(object_data.items())
        while to_evaluate:
            (field, field_type), value = to_evaluate.pop(0)

            if value == EMPTY_COLLECTION:
                continue

            if isinstance(field_type, DiffObjectBuilder._FunctionCallFieldType):
                # Do not evaluate function calls as part of objects.
                continue

            if ISP(field_type):
                evaluated_object[field] = value

            elif field_type is DiffObjectBuilder._DictKeyResolve:
                field_info: DiffObjectBuilder._DictKeyResolve = field
                # The field is a dict key that should also be resolved (for dict keys that are objects).
                resolved_key = self.build(field_info.field, time, field_info.field_type, line_no)
                resolved_value = self.build(field_info.value, time, field_info.value_type, line_no)
                evaluated_object[resolved_key] = resolved_value

            # Handle with postponed operations.
            elif field_type == Postpone:
                # Re-evaluate object after postponed operation handled.
                evaluated_object, to_evaluate = self.__build_postponed(evaluated_object, line_no, time, to_evaluate,
                                                                       value)
                evaluated_object.clear()
            else:
                # Build the value (should be an object to build).
                evaluated_value = self.build(value, time, field_type)
                # Add attribute.
                if isinstance(field, str):
                    setattr(evaluated_object, field, evaluated_value)
                # Add to dict.
                evaluated_object[field] = evaluated_value

        if BuiltinCollectionsUtils.is_builtin_collection_type(object_type):
            evaluated_object = object_type(evaluated_object.values())
        return evaluated_object

    def __build_postponed(self, evaluated_object, line_no, t, to_evaluate, value):
        manip_name = value.manip_name
        col_type = value.builtin_type
        arg = value.arg_value
        arg_type = value.arg_type
        evaluated_arg = self.build(arg, t, arg_type, line_no=line_no) if arg != EMPTY else arg
        to_evaluate = list(
            BuiltinCollectionsUtils.update_dict_object_with_builtin_method(evaluated_object, col_type, manip_name,
                                                                           evaluated_arg).items()) + to_evaluate
        return evaluated_object, to_evaluate

    def _get_data_from_named(self, name: str, time: Time, line_no: Optional[int] = -1) -> Tuple[
        Type, Union[ObjectId, None], Union[RangeDict, Any, None]]:

        not_found_ret_value = NoneType, None, None

        is_primitive = name in self._named_primitives
        line_no_exist = line_no > -1

        if is_primitive:
            named_collection: _NAMED_PRIMITIVES_DATA_TYPE = self._named_primitives
        elif name in self._named_objects:
            named_collection: _NAMED_OBJECTS_DATA_TYPE = self._named_objects
        else:
            return not_found_ret_value

        if line_no_exist and line_no not in named_collection[name]:
            return not_found_ret_value

        named_data_and_type = named_collection[name][line_no] if line_no_exist \
            else list(named_collection[name].values())[0]

        if is_primitive:
            named_type, named_data = named_data_and_type
            if ISP(named_type):
                # Item is a primitive, return it.
                return named_type, None, named_data[time][name, named_type] \
                    if time in named_data and (name, named_type) in named_data[time] else None
            else:
                # TODO: Can this branch be reached?
                return not_found_ret_value
        else:
            if time not in named_data_and_type:
                named_type, object_id = named_data_and_type[DiffObjectBuilder.__get_last_time(named_data_and_type)]
            else:
                named_type, object_id = named_data_and_type[time]
            return named_type, object_id, self._data[object_id]

    @staticmethod
    def __initial_range(t: Time):
        return Range(t, t, include_end=True)

    def _construct(self):
        for rk, rv in sorted(
                self.archive.flatten_and_filter(
                    [lambda vv: vv.key.stub_name in {__AS__.__name__, __BMFCS__.__name__, __FC__.__name__},
                     lambda vv: '__PALADIN_' not in vv.expression]),
                key=lambda t: t[1].time):
            object_data: RangeDict = self.__add_to_data(rk, rv)
            if rk.kind in {Archive.Record.StoreKind.VAR, Archive.Record.StoreKind.FUNCTION_CALL}:
                self.__add_to_named_objects(rv, object_data)

    def __add_to_data(self, rk: Archive.Record.RecordKey, rv: Archive.Record.RecordValue) -> RangeDict:
        t: Time = rv.time
        object_id: ObjectId = rk.container_id
        field: Union[str, ObjectId] = rk.field

        if object_id not in self._data:
            return self.__add_first_value(object_id, t, field, rv.value, rv.rtype, rv.key.kind)

        object_id_data: RangeDict = self._data[object_id]
        last_range: Range = self._last_range[object_id]
        key: Tuple[str, Type] = field, rv.rtype
        last_object_value = object_id_data[last_range]

        # Same value in a new time.
        if key in last_object_value and last_object_value[key] == rv.value:
            # Extend range.
            self._last_range[object_id] = DiffObjectBuilder.__extend_range(object_id_data, last_range, t)

        # New field for the same time as the last insertion.
        elif key not in last_object_value and t == last_range.end:
            object_id_data[last_range] = DiffObjectBuilder.__update_value(last_object_value, field, rv.value, rv.rtype,
                                                                          rv.key.kind)

        # New field in a new time, create a different value for object id in new time t.
        else:
            # Finalize last range if needed.
            if t - 1 not in object_id_data:
                DiffObjectBuilder.__extend_range(object_id_data, last_range, t - 1)

            # Create a new range.
            rng: Range = DiffObjectBuilder.__initial_range(t)

            # Update the object.
            object_id_data[rng] = DiffObjectBuilder.__update_value(last_object_value, field, rv.value,
                                                                   rv.rtype, rv.key.kind)
            self._last_range[object_id] = rng

        return object_id_data

    @staticmethod
    def __get_last_time(rd: RangeDict):
        return sorted(reduce(lambda ll, l: ll + l, [[y.end for y in x] for x in rd.ranges()]), reverse=True)[0]

    @staticmethod
    def __add_to_range_dict(rd: RangeDict, t: Time, value: Any):

        last_time = DiffObjectBuilder.__get_last_time(rd)
        if rd[last_time] == value:
            rng: Range = rd.getrange(last_time)
            DiffObjectBuilder.__extend_range(rd, rd.getrange(last_time), t)
        else:
            # Extend last range.
            DiffObjectBuilder.__extend_range(rd, rd.getrange(last_time), t - 1)
            rng: Range = DiffObjectBuilder.__initial_range(t)
            rd[rng] = value

        return rng

    def __add_first_value(self, object_id: ObjectId, t: Time, field: str, value: Any, _type: Type,
                          kind: Archive.Record.StoreKind):
        self._last_range[object_id] = DiffObjectBuilder.__initial_range(t)
        self._data[object_id] = RangeDict(
            [(self._last_range[object_id], DiffObjectBuilder.__update_value(None, field, value, _type, kind))])

        return self._data[object_id]

    @staticmethod
    def __is_in_data(data: RangeDict, t: Time, field: str, value: Any) -> bool:
        return field in data and data[t][field] == value

    @staticmethod
    def __update_value(obj: Any, field: Union[str, Any, ObjectId], value: Any, _type: Union[Type, Tuple[Type, Type]],
                       kind: Archive.Record.StoreKind) -> Any:
        new_obj = copy.copy(obj) if obj else {}

        if kind == Archive.Record.StoreKind.BUILTIN_MANIP:
            new_obj = BuiltinCollectionsUtils \
                .create_dict_object_with_postponed_builtin_collection_methods(new_obj, _type, field, value[0], value[1])
        elif kind == Archive.Record.StoreKind.UNAMED_OBJECT:
            new_obj = {}
        elif kind == Archive.Record.StoreKind.DICT_ITEM:
            key_type, value_type = _type
            if ISP(key_type):
                new_obj[(field, value_type)] = value
            else:
                new_obj[
                    DiffObjectBuilder._DictKeyResolve(key_type, field, _type,
                                                      value), DiffObjectBuilder._DictKeyResolve] = None
        elif kind == Archive.Record.StoreKind.FUNCTION_CALL:
            new_obj[(field, DiffObjectBuilder._FunctionCallFieldType(_type))] = value
        else:
            new_obj[(field, _type)] = value
        return new_obj

    @staticmethod
    def __extend_range(object_id_data: RangeDict, last_range: Range, new_time: Time) -> Range:
        updated_last_range = Range(start=last_range.start, end=new_time if new_time > 0 else 0,
                                   include_start=True, include_end=True)

        object_id_data[updated_last_range] = object_id_data[last_range]
        return updated_last_range

    def __add_to_named_objects(self, rv: Archive.Record.RecordValue, object_data: RangeDict):
        is_primitive = ISP(rv.rtype) and rv.rtype != NoneType
        self.__init_named_collection_for_expression(self._named_primitives if is_primitive else self._named_objects, rv)

        if is_primitive:
            self._named_primitives[rv.expression][rv.line_no] = rv.rtype, object_data
        else:
            if rv.line_no not in self._named_objects[rv.expression]:
                self._named_objects[rv.expression][rv.line_no] = RangeDict(
                    [(self.__initial_range(rv.time), (rv.rtype, rv.value))])
            else:
                DiffObjectBuilder.__add_to_range_dict(self._named_objects[rv.expression][rv.line_no], rv.time,
                                                      (rv.rtype, rv.value))

    @staticmethod
    def __init_named_collection_for_expression(
            named_collection: Union[_NAMED_PRIMITIVES_DATA_TYPE, _NAMED_OBJECTS_DATA_TYPE],
            rv: Archive.Record.RecordValue):
        if rv.expression not in named_collection:
            named_collection[rv.expression] = {}

    def _build_iterator(self, obj: Union[str, ObjectId], line_no: Optional[LineNo] = -1) -> \
            Optional[Iterator[Tuple[Time, Any]]]:
        for t in range(0, self.archive.last_time):
            yield t, self.build(obj, t, type(obj), line_no)

        return None

    def __get_latest_object_data(self, object_id: ObjectId, time: Time, _type: Type = Any) -> \
            Optional[RangeDict]:

        if time in self._data[object_id]:
            return self._data[object_id][time]

        try:
            first, last = DiffObjectBuilder.get_edge_times(self._data[object_id])
            if time >= last:
                return self._data[object_id][last]
        except KeyError:
            return None

    @staticmethod
    def get_edge_times(rd: RangeDict) -> Tuple[Time, Time]:
        all_ranges = reduce(lambda rr, r: rr + r, rd.ranges())
        return min(all_ranges).start, max(all_ranges).end
