import ast
from ast import NodeVisitor
from dataclasses import dataclass
from typing import *

from frozendict import frozendict
from ranges import Range, RangeDict

from archive.archive import Archive, Rv
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, ObjectId
from ast_common.ast_common import str2ast, ast2str
from common.common import ISP
from stubs.stubs import __AS__, __BMFCS__


class Object(dict):
    pass


class DiffObjectBuilder(object):

    def __init__(self, archive: Archive):
        self.archive: Archive = archive
        self.data: Dict[ObjectId, RangeDict] = {}
        self._last_range: Dict[ObjectId, Range] = {}
        self._built_objects: Dict[(ObjectId, Time), Any] = {}
        self._construct()

    def search(self, object_id: ObjectId, t: Time) -> Union[List, Dict, Tuple, Set, Any, frozendict]:
        if (object_id, t) in self._built_objects:
            return self._built_objects[object_id, t]

        obj: Any = self.data[object_id][t]

        found: Union[Dict, List, Set, Tuple, Any] = None
        if isinstance(obj, Dict):
            found = {f: v if v not in self.data[object_id] else self.search(v, t) for f, v in obj.items()}
        else:
            found = [v if v not in self.data[object_id] else self.search(v, t) for v in obj]

        if isinstance(obj, Set):
            found = set(found)

        if isinstance(obj, Tuple):
            found = tuple(found)

        self._built_objects[object_id, t] = found
        return found

    @staticmethod
    def __initial_range(t: Time):
        return Range(t, t, include_end=True)

    def _construct(self):
        for rk, rv in sorted(
                self.archive.flatten_and_filter([lambda vv: vv.key.stub_name in {__AS__.__name__, __BMFCS__.__name__},
                                                 lambda vv: '__PALADIN_' not in vv.expression]),
                key=lambda t: t[1].time):
            self.__add_to_data(rv.time, rk.container_id, rk.field, rv)

    def __add_to_data(self, t: Time, object_id: ObjectId, field: str, rv: Archive.Record.RecordValue):
        if object_id not in self.data:
            self.__add_first_value(object_id, t, field, rv.value, rv.rtype, rv.key.kind)
            return

        object_id_data: RangeDict = self.data[object_id]

        last_range: Range = self._last_range[object_id]

        if field in object_id_data[last_range] and object_id_data[last_range][field] == rv.value:
            self.__extend_range(object_id_data, last_range, t)
        else:
            # Create a new range.
            rng: Range = DiffObjectBuilder.__initial_range(t)

            # Update the object.
            object_id_data[rng] = DiffObjectBuilder.__update_object(object_id_data[last_range], field, rv.value,
                                                                    rv.rtype, rv.key.kind)
            self._last_range[object_id] = rng

    def __extend_range(self, object_id_data: RangeDict, last_range: Range, t: Time) -> Any:
        value: Any = object_id_data.pop(last_range)
        # Extend the range.
        new_range = last_range
        new_range.end = t
        new_range.include_end = True
        object_id_data[new_range] = value

    def __add_first_value(self, object_id: ObjectId, t: Time, field: str, value: Any, _type: Type,
                          kind: Archive.Record.StoreKind):
        self._last_range[object_id] = DiffObjectBuilder.__initial_range(t)
        self.data[object_id] = RangeDict(
            [(self._last_range[object_id], DiffObjectBuilder.__update_object(None, field, value, _type, kind))])

    @staticmethod
    def __is_in_data(data: RangeDict, t: Time, field: str, value: Any) -> bool:
        return field in data and data[t][field] == value

    @staticmethod
    def __update_object(obj: Any, field: str, value: Any, _type: Type, k: Archive.Record.StoreKind) -> Any:
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
        return obj

    def find_by_line_no(self, expression: str, line_no: int, time: int = -1) -> Dict[int, List[Rv]]:
        """
        Find the values of an expression in the archive throughout its time, where the names are bounded to a scope
        of a line no.
        @param expression: The expression to look for.
        @param line_no: The line no to bound a scope for.
        @param time:
        @return:
        """
        scope = self.archive.get_scope_by_line_no(line_no) if line_no != -1 else -1

        def _find_by_name_and_container_id(name: str, container_id: int) -> List[Archive.Record.RecordValue]:
            return [r[1] for r in self.archive.flatten_and_filter(
                lambda
                    vv: vv.key.container_id == container_id and vv.key.field == name and vv.time <= time)]

        def _find_by_name(name: str) -> List[Archive.Record.RecordValue]:
            return [r[1] for r in self.archive.flatten_and_filter(lambda vv: vv.key.field == name and vv.time <= time)]

        @dataclass
        class NodeFinder(NodeVisitor):
            def __init__(_self, archive: 'Archive'):
                _self.archive = archive
                _self.values = {}

            def visit_Subscript(_self, node: ast.Subscript) -> Any:
                # TODO: Handle.
                raise NotImplementedError('TODO: Fix.')

            def visit_Name(_self, node: ast.Name) -> Any:
                _self.values[node.id] = {
                    rv.time:
                        rv.value if ISP(rv.rtype) else self.search(rv.value, rv.time)
                    for rv in
                    (_find_by_name_and_container_id(node.id, scope) if scope != -1 else _find_by_name(node.id))
                }

            def visit_Attribute(_self, node: ast.Attribute) -> Any:
                # Resolve value (lhs of "lhs.rhs").
                _self.visit(node.value)
                value_str = ast2str(node.value)
                attr_str = ast2str(node)
                _self.values[attr_str] = {}

                if value_str not in _self.values:
                    return None

                # Add attribute's value.
                for t, v in _self.values[value_str].items():
                    if type(v) is int:
                        # v is probably an object id.
                        obj = self.search(v, t)
                        if obj is None:
                            # TODO: I don't know what to do here...
                            continue
                        attr = obj[0][node.attr]
                        pass
                    else:
                        attr = v[node.attr]

                    _self.values[attr_str][t] = attr

            def visit(_self, node: ast.AST) -> 'NodeFinder':
                super(NodeFinder, _self).visit(node)
                return _self

        return NodeFinder(self.archive).visit(str2ast(expression)).values
