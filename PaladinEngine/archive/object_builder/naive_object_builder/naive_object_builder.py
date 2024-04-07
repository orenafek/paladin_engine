from typing import Optional, Type, Any, Dict

from common.attributed_dict import AttributedDict
from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import ContainerId, LineNo, Identifier, \
    Time
from archive.object_builder.object_builder import ObjectBuilder
from builtin_manipulation_calls.builtin_manipulation_calls import BuiltinCollectionsUtils, EMPTY, EMPTY_COLLECTION
from common.common import ISP


class NaiveObjectBuilder(ObjectBuilder):

    def build(self, item: Identifier, time: Time, _type: Type = Any, line_no: Optional[LineNo] = -1) -> Any:
        records = self._find_records(item, time, line_no)

        if not records:
            return None

        rk, rv = records[-1]

        if ISP(rv.rtype):
            return rv.value

        # Item is a complex object.
        return self._build_object(rv.value, time, rv.rtype if not isinstance(rv.rtype, tuple) else rv.rtype[1], line_no)

    def _build_object(self, item: Optional[ContainerId], time: Time,
                      rtype: Type, line_no: Optional[LineNo] = -1) -> Any:

        if ISP(rtype):
            return item

        records = sorted(self.archive.flatten_and_filter(
            [Archive.Filters.AS_OR_BMFCS_FILTER, Archive.Filters.CONTAINER_ID_EQUALS(item),
             Archive.Filters.TIME_EQUAL_OR_LATER_FILTER(time)] +
            ([Archive.Filters.LINE_NO_FILTER(line_no)] if line_no > -1 else [])), key=lambda r: r[1].time)

        object_data = AttributedDict()
        for rk, rv in records:
            match rk.kind:
                case Archive.Record.StoreKind.DICT_ITEM:
                    field_type, value_type = rv.rtype
                case Archive.Record.StoreKind.LIST_ITEM:
                    field_type, value_type = int, rv.rtype
                case _:
                    field_type, value_type = str, rv.rtype

            if ISP(field_type):
                field = rk.field
            else:
                field = self._build_object(rk.field, time, field_type, line_no)

            if BuiltinCollectionsUtils.is_builtin_collection_type(rtype) and rv.value == EMPTY_COLLECTION:
                # Empty collection rv, no need to do anything for this rv.
                continue

            if rk.kind == Archive.Record.StoreKind.BUILTIN_MANIP:
                arg_type, arg_value = rv.value

                if arg_value == EMPTY:
                    evaluated_arg = EMPTY
                elif ISP(arg_type):
                    evaluated_arg = arg_value
                else:
                    evaluated_arg = self.build(arg_value, time, arg_type, line_no=line_no)

                object_data = BuiltinCollectionsUtils.update_dict_object_with_builtin_method(object_data, rv.rtype,
                                                                                             rk.field, evaluated_arg)
            else:
                object_data[field] = self._build_object(rv.value, time, value_type, line_no)

        if BuiltinCollectionsUtils.is_builtin_collection_type(rtype):
            object_data = rtype(object_data.values())

        if isinstance(object_data, Dict):
            ObjectBuilder._add_attributes(object_data)

        return object_data

    def get_type(self, item: Identifier, time: Time, line_no: Optional[LineNo] = -1) -> Optional[Type]:
        pass

    def get_change_times(self, name: str, line_no: LineNo = -1):
        pass

    def get_line_no_by_name_and_container_id(self, name: str, container_id: ContainerId = -1) -> LineNo:
        pass

    def _find_records(self, item: Identifier, time: Time, line_no: LineNo):
        stub_filter = Archive.Filters.OR(Archive.Filters.AS_OR_BMFCS_FILTER, Archive.Filters.FC_FILTER)
        identifier_filter = Archive.Filters.OR(Archive.Filters.FIELD_EQUALS(item), Archive.Filters.VALUE_FILTER(item))
        kind_filter = lambda vv: (vv.key.kind == Archive.Record.StoreKind.FUNCTION_CALL and vv.time == time) or (
                vv.key.kind != Archive.Record.StoreKind.FUNCTION_CALL and vv.time <= time)

        line_no_filter = Archive.Filters.LINE_NO_FILTER(line_no) if line_no > -1 else lambda vv: True
        base_filters = [stub_filter, identifier_filter, kind_filter]

        records = self.archive.flatten_and_filter(base_filters + [line_no_filter])

        container_ids_and_fields = list(map(lambda r: (r[0].container_id, r[0].field), records))

        scoped_records = self.archive.flatten_and_filter(
            base_filters + [lambda vv: (vv.key.container_id, vv.key.field) in container_ids_and_fields])

        return sorted(list(set(records + scoped_records)), key=lambda r: r[1].time)
