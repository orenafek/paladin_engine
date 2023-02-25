import copy
from functools import reduce
from typing import *

from ranges import Range, RangeDict

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, ObjectId, LineNo
from archive.object_builder.object_builder import ObjectBuilder
from builtin_manipulation_calls.builtin_manipulation_calls import IS_BUILTIN_MANIPULATION_TYPE, \
    UPDATE_DICT_OBJECT_WITH_MANIPULATION_METHOD, Postpone, EMPTY, \
    CREATE_POSTPONED_DICT_OBJECT_WITH_MANIPULATION_METHOD
from common.common import ISP
from stubs.stubs import __AS__, __BMFCS__


class Object(dict):
    pass


class DiffObjectBuilder(ObjectBuilder):
    ObjectEntry = Tuple[Type, Any]

    class AttributedDict(Dict):
        pass

    def __init__(self, archive: Archive):
        self.archive: Archive = archive
        self._data: Dict[ObjectId, RangeDict] = {}
        self._last_range: Dict[ObjectId, Range] = {}
        self._built_objects: Dict[Tuple[ObjectId, Time], Any] = {}
        self._named_objects: Dict[str, Dict[LineNo, Tuple[ObjectId, Type]]] = {}
        self._construct()

    def build(self, item: Union[str, ObjectId], t: Time, _type: Type = Any, line_no: Optional[LineNo] = -1) -> Any:
        # Extract Object-Id from named object if item is a string.
        obj, _type = self._get_object_id_by_name(item, line_no) if isinstance(item, str) else (item, _type)

        # If the object asked to be built is a primitive, or it's not an object in the data
        if ISP(_type) or obj not in self._data:
            return obj

        object_id = obj
        if (object_id, t) in self._built_objects:
            # If its already built, return it.
            return self._built_objects[object_id, t]

        if t not in self._data[object_id]:
            # If there is no entry for this object in time t, get the closest result possible.
            return self.__get_latest_value_before_time(object_id, t, _type, line_no)

        # Extract the object's building data.
        obj_data = self._data[object_id][t]

        evaluated_object = DiffObjectBuilder.AttributedDict()

        to_evaluate = list(obj_data.items())
        while to_evaluate:
            (field, field_type), value = to_evaluate.pop(0)

            if ISP(field_type):
                evaluated_object[field] = value

            # Handle with postponed operations.
            elif field_type == Postpone:
                # Re-evaluate object after postponed operation handled.
                evaluated_object, to_evaluate = self.__build_postponed(evaluated_object, line_no, t, to_evaluate, value)
                evaluated_object.clear()
            else:
                # Build the value (should be an object to build).
                evaluated_value = self.build(value, t)
                # Add attribute.
                setattr(evaluated_object, field, evaluated_value)
                # Add to dict.
                evaluated_object[field] = evaluated_value

        if IS_BUILTIN_MANIPULATION_TYPE(_type):
            evaluated_object = _type(evaluated_object.values())

        self._built_objects[(object_id, t)] = evaluated_object
        return evaluated_object

    def __build_postponed(self, evaluated_object, line_no, t, to_evaluate, value):
        manip_name = value.manip_name
        col_type = value._type
        arg = value.value
        evaluated_arg = self.build(arg, t, list, line_no) if arg != EMPTY else arg
        to_evaluate = list(UPDATE_DICT_OBJECT_WITH_MANIPULATION_METHOD(evaluated_object, col_type, manip_name,
                                                                       evaluated_arg).items()) + to_evaluate
        return evaluated_object, to_evaluate

    def _get_object_id_by_name(self, name: str, line_no: Optional[int] = -1) -> Optional[Tuple[ObjectId, Type]]:
        if name not in self._named_objects:
            return None, Any

        if line_no > -1:
            return self._named_objects[name][line_no]

        else:
            return list(self._named_objects[name].values())[0]

    @staticmethod
    def __initial_range(t: Time):
        return Range(t, t, include_end=True)

    def _construct(self):
        for rk, rv in sorted(
                self.archive.flatten_and_filter([lambda vv: vv.key.stub_name in {__AS__.__name__, __BMFCS__.__name__},
                                                 lambda vv: '__PALADIN_' not in vv.expression]),
                key=lambda t: t[1].time):
            self.__add_to_data(rv.time, rk.container_id, rk.field, rv)
            if rk.kind == Archive.Record.StoreKind.VAR:
                self.__add_to_named_objects(rv)

    def __add_to_data(self, t: Time, object_id: ObjectId, field: str, rv: Archive.Record.RecordValue):
        if object_id not in self._data:
            self.__add_first_value(object_id, t, field, rv.value, rv.rtype, rv.key.kind)
            return

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

    def __add_first_value(self, object_id: ObjectId, t: Time, field: str, value: Any, _type: Type,
                          kind: Archive.Record.StoreKind):
        self._last_range[object_id] = DiffObjectBuilder.__initial_range(t)
        self._data[object_id] = RangeDict(
            [(self._last_range[object_id], DiffObjectBuilder.__update_value(None, field, value, _type, kind))])

    @staticmethod
    def __is_in_data(data: RangeDict, t: Time, field: str, value: Any) -> bool:
        return field in data and data[t][field] == value

    @staticmethod
    def __update_value(obj: Any, field: str, value: Any, _type: Type, kind: Archive.Record.StoreKind) -> Any:
        new_obj = copy.copy(obj) if obj else {}

        if kind == Archive.Record.StoreKind.BUILTIN_MANIP:
            new_obj = CREATE_POSTPONED_DICT_OBJECT_WITH_MANIPULATION_METHOD(new_obj, _type, field, value)
        else:
            new_obj[(field, _type)] = value
        return new_obj

    @staticmethod
    def __construct_object(obj: Dict[str, Any], field: str, value: Any, _type: Type,
                           k: Archive.Record.StoreKind) -> 'DiffObjectBuilder.ObjectEntry':
        if k == Archive.Record.StoreKind.BUILTIN_MANIP:
            if not obj:
                obj = _type()
            obj.__getattribute__(field)(value)

        elif k is Archive.Record.StoreKind.DICT_ITEM:
            if not obj:
                obj = {}

            obj[field] = value

        elif k is Archive.Record.StoreKind.VAR:
            if not obj:
                obj = Object()

            setattr(obj, field, value)
            obj[field] = value

        elif k == Archive.Record.StoreKind.LIST_ITEM:
            if not obj:
                obj = []
            if field < len(obj):
                obj[field] = value
            else:
                obj.insert(field, value)

        elif k == Archive.Record.StoreKind.SET_ITEM:
            if not obj:
                obj = set()
            obj.add(value)

        elif k == Archive.Record.StoreKind.TUPLE_ITEM:
            obj = (*obj, value) if obj else (value,)

        return _type, obj

    @staticmethod
    def __extend_range(object_id_data: RangeDict, last_range: Range, new_time: Time) -> Range:
        updated_last_range = Range(start=last_range.start, end=new_time if new_time > 0 else 0,
                                   include_start=True, include_end=True)

        object_id_data[updated_last_range] = object_id_data[last_range]
        return updated_last_range

    def __add_to_named_objects(self, rv: Archive.Record.RecordValue):
        if rv.expression not in self._named_objects:
            self._named_objects[rv.expression] = {}

        self._named_objects[rv.expression][rv.line_no] = rv.value, rv.rtype

    def _build_iterator(self, obj: Union[str, ObjectId], line_no: Optional[LineNo] = -1) -> \
            Optional[Iterator[Tuple[Time, Any]]]:
        for t in range(0, self.archive.last_time):
            yield t, self.build(obj, t, line_no)

        return None

    def __get_latest_value_before_time(self, object_id: ObjectId, time: Time, _type: Type = Any,
                                       line_no: LineNo = -1) -> Optional[Any]:
        try:
            first, last = DiffObjectBuilder.get_edge_times(self._data[object_id])
            if time >= last:
                return self.build(object_id, last, _type, line_no)
        except KeyError:
            return None

    @staticmethod
    def get_edge_times(rd: RangeDict) -> Tuple[Time, Time]:
        all_ranges = reduce(lambda rr, r: rr + r, rd.ranges())
        return min(all_ranges).start, max(all_ranges).end
