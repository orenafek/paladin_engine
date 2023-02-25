from _ast import AST, Name, Attribute, Subscript
from ast import parse, NodeVisitor
from dataclasses import dataclass
from typing import *

from frozendict import frozendict

from archive.archive import Archive, Rk, Rv
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import LineNo, Time
from archive.object_builder.object_builder import ObjectBuilder
from ast_common.ast_common import ast2str
from builtin_manipulation_calls.builtin_manipulation_calls import __BUILTIN_COLLECTIONS__
from common.common import ISP


class RecursiveObjectBuilder(ObjectBuilder):
    SUPPOERTED_BUILTIN_COLLECTION_TYPES = {*__BUILTIN_COLLECTIONS__}

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
                                                       lambda vv: RecursiveObjectBuilder.time_filter(vv, time),
                                                       # lambda vv: vv not in self.used_records
                                                       ]), key=lambda t: t[1].time)

    def _build(self, object_id: int, rtype: type = Any, time: int = -1) -> Any:
        try:
            # Extract from built objects' cache.
            obj = self.built_objects[object_id] if object_id in self.built_objects else None

            relevant_records = self.get_relevant_records(object_id, time)

            if not relevant_records:
                # The object is already built and there are no relevant records to update its value.
                if obj is not None:
                    return obj

                # The object is not already built and no relevant records.
                if rtype in RecursiveObjectBuilder.SUPPOERTED_BUILTIN_COLLECTION_TYPES:
                    # The object should be an empty builtin collection
                    return rtype()

                # Otherwise, no object has been built and no relevant records to update it.
                return None

            while relevant_records:
                k, v = relevant_records.pop()
                value = v.value if ISP(v.rtype) else self._build(v.value, v.rtype, time)
                self.used_records.append(v)

                obj = RecursiveObjectBuilder.update_object_by_kind(k, obj, rtype, value)

            if isinstance(obj, dict):
                obj = frozendict(obj)

            self.built_objects[object_id] = obj
            return obj

        except (TypeError, IndexError):
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

    def build(self, expression: str, time: Time = -1, line_no: LineNo = -1) -> List[Rv]:
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
            return [r[1] for r in self.archive.flatten_and_filter(
                lambda
                    vv: vv.key.container_id == container_id and vv.key.field == name and vv.time <= time)]

        def _find_by_name(name: str) -> List['Archive.Record.RecordValue']:
            return [r[1] for r in self.archive.flatten_and_filter(lambda vv: vv.key.field == name and vv.time <= time)]

        @dataclass
        class NodeFinder(NodeVisitor):
            def __init__(self, builder: RecursiveObjectBuilder):
                self.archive = archive
                self.values = {}
                self.builder: RecursiveObjectBuilder = builder

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
                        obj = self.builder._build(v, time=time)
                        # noinspection PySimplifyBooleanCheck
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
                # noinspection PyTypeChecker
                self.values[node.id] = [rv.value if ISP(rv.rtype) else self.builder._build(rv.value, rv.rtype, time)
                                        for rv in (_find_by_name_and_container_id(node.id, scope)
                                                   if scope != -1 else _find_by_name(node.id))
                                        ]

            def visit(self, node: AST) -> 'NodeFinder':
                super(NodeFinder, self).visit(node)
                return self

        return list(NodeFinder(self).visit(parse(expression).body[0]).values)

    def get_scope_by_line_no(self, line_no: int) -> int:
        """
            Returns the "scope", meaning the container_id (id of the frame) of variables (not object's fields) that
            are referenced in a line_no.
        :param line_no: The line no.
        :return: scope.
        """
        # Get all records by time.
        record_values_by_time = [rv for _, rv in self.archive.flat_and_sort_by_time()]

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
