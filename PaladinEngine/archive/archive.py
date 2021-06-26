"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import tabulate
import pandas as pd
import prettytable

from PaladinEngine.conf.engine_conf import ARCHIVE_PRETTY_TABLE_MAX_ROW_LENGTH


class Archive(object):
    class Record(object):
        @dataclass
        class RecordKey(object):
            container_id: int
            field: str

            def __hash__(self) -> int:
                return hash(hash(self.container_id) + hash(self.field))

            def __eq__(self, o: object) -> bool:
                return isinstance(o, Archive.Record.RecordKey) \
                       and o.field == self.field \
                       and o.container_id == self.container_id

            def __str__(self) -> str:
                return f'{self.field}(c:{self.container_id})'

            def to_json(self):
                return self.container_id, self.field

        @dataclass
        class RecordValue(object):
            rtype: type
            value: object
            expression: str
            line_no: int
            extra: str = ''
            time: int = -1

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

            def to_json(self):
                return (self.rtype.__name__,
                        self.value,
                        self.expression,
                        self.line_no,
                        self.time,
                        self.extra)

    def __init__(self) -> None:
        self.records = {}
        self._time = -1
        self._should_record = True

    @property
    def time(self):
        self._time += 1
        return self._time

    @property
    def current_time(self):
        self.time += 1
        return self.time

    def store(self, record_key: Record.RecordKey, record_value: Record.RecordValue):
        if not self._should_record:
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

            def represent(o: object) -> str:
                if type(o) in [str, int, float, bool, complex]:
                    return str(o)

                return f'{id(o)}'

            flat_records = [
                (
                    k.container_id,
                    k.field,
                    str(v.rtype.__name__),
                    represent(v.value).replace('\n', ' '),
                    v.expression,
                    v.line_no,
                    v.time,
                    v.extra
                )
                for k, vv in list(self.records.items()) for v in vv
            ]

            return header_row, flat_records

        except RuntimeError as e:
            print(e)

    def to_pickle(self):
        import pickle
        return pickle.dumps(self.records)

    def __repr__(self):
        header, rows = self.to_table()
        data_frame = pd.DataFrame(columns=header, data=rows)
        return data_frame.to_markdown(index=True)

    def search(self, expression: str):
        pass

    def __str__(self):
        return self.__repr__()

    def pause_record(self):
        self._should_record = False

    def resume_record(self):
        self._should_record = True
