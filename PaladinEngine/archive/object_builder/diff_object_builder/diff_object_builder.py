import copy
from functools import reduce
from typing import *

from ranges import Range, RangeDict

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, ObjectId, LineNo
from archive.object_builder.object_builder import ObjectBuilder
from builtin_manipulation_calls.builtin_manipulation_calls import IS_BUILTIN_MANIPULATION_TYPE
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

    def build(self, item: Union[str, ObjectId], t: Time, line_no: Optional[LineNo] = -1) -> Any:

        obj, _type = (item, Any) if isinstance(item, ObjectId) else self._get_object_id_by_name(item, line_no)

        if ISP(_type):
            return obj

        object_id = obj
        if (object_id, t) in self._built_objects:
            return self._built_objects[object_id, t]

        if t not in self._data[object_id]:
            return self.__get_latest_value_before_time(object_id, t)

        obj = self._data[object_id][t]

        evaluated_object = DiffObjectBuilder.AttributedDict()

        for (field, _type), value in obj.items():
            if ISP(_type):
                evaluated_value = value
            elif IS_BUILTIN_MANIPULATION_TYPE(_type):
                # TODO: Deel with collections.
                pass
            else:
                evaluated_value = self.build(value, t)
                # Add attribute.
                setattr(evaluated_object, field, evaluated_value)

            # Add to dict.
            evaluated_object[field] = evaluated_value

        self._built_objects[(object_id, t)] = evaluated_object
        return evaluated_object

    def _get_object_id_by_name(self, name: str, line_no: Optional[int] = -1) -> Optional[Tuple[ObjectId, Type]]:
        if name not in self._named_objects:
            return None

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
            self.__add_first_value(object_id, t, field, rv.value, rv.rtype)
            return

        object_id_data: RangeDict = self._data[object_id]

        last_range: Range = self._last_range[object_id]

        key: Tuple[str, Type] = field, rv.rtype
        if key in object_id_data[last_range] and object_id_data[last_range][key] == rv.value:
            # Extend range.
            self._last_range[object_id] = DiffObjectBuilder.__extend_range(object_id_data, last_range, t)
        else:
            # Finalize last range if needed.
            if t - 1 not in object_id_data:
                DiffObjectBuilder.__extend_range(object_id_data, last_range, t - 1)

            # Create a new range.
            rng: Range = DiffObjectBuilder.__initial_range(t)

            # Update the object.
            object_id_data[rng] = DiffObjectBuilder.__update_value(object_id_data[last_range], field, rv.value,
                                                                   rv.rtype)
            self._last_range[object_id] = rng

    def __add_first_value(self, object_id: ObjectId, t: Time, field: str, value: Any, _type: Type):
        self._last_range[object_id] = DiffObjectBuilder.__initial_range(t)
        self._data[object_id] = RangeDict(
            [(self._last_range[object_id], DiffObjectBuilder.__update_value(None, field, value, _type))])

    @staticmethod
    def __is_in_data(data: RangeDict, t: Time, field: str, value: Any) -> bool:
        return field in data and data[t][field] == value

    @staticmethod
    def __update_value(obj: Any, field: str, value: Any, _type: Type) -> Any:
        new_obj = copy.copy(obj) if obj else {}
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

    def __get_latest_value_before_time(self, object_id: ObjectId, time: Time) -> Optional[Any]:
        try:
            first, last = DiffObjectBuilder.get_edge_times(self._data[object_id])
            if time >= first:
                return self._built_objects[object_id, last]
        except KeyError:
            return None

    @staticmethod
    def get_edge_times(rd: RangeDict) -> Tuple[Time, Time]:
        all_ranges = reduce(lambda rr, r: rr + r, rd.ranges())
        return min(all_ranges).start, max(all_ranges).end
