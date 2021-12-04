"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""
from dataclasses import dataclass
from typing import Optional, Iterable, Dict

import pandas as pd


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
    class Record(object):
        @dataclass
        class RecordKey(object):
            container_id: int
            field: str
            stub_name: str

            def __hash__(self) -> int:
                return hash(hash(self.container_id) + hash(self.field))

            def __eq__(self, o: object) -> bool:
                return isinstance(o, Archive.Record.RecordKey) \
                       and o.field == self.field \
                       and o.container_id == self.container_id \
                       and o.stub_name == self.stub_name

            def __str__(self) -> str:
                return f'{self.field}(c:{self.container_id})'

            def to_json(self):
                return self.container_id, self.field

        @dataclass
        class RecordValue(object):
            key: object
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

            def to_json(self):
                return (self.rtype.__name__,
                        represent(self.value),
                        self.expression,
                        self.line_no,
                        self.time,
                        self.extra)

    def __init__(self) -> None:
        self.records: Dict[Archive.Record.RecordKey, Archive.Record.RecordValue] = {}
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

            flat_records = [
                (
                    k.container_id,
                    k.field,
                    k.stub_name,
                    id(v.key),
                    str(v.rtype.__name__),
                    # represent(v.value).replace('\n', ' '),
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

    @property
    def record_values_sorted_by_time(self):
        return sorted([rv for rk in self.records for rv in self.records[rk]],
                      key=lambda r: r.time)

    def to_pickle(self):
        import pickle
        return pickle.dumps(self.records)

    def __repr__(self):
        header, rows = self.to_table()
        data_frame = pd.DataFrame(columns=header, data=rows)
        return data_frame.to_markdown(index=True)

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

        return ''

    def search(self, expression: str, frame: dict = None) -> Optional[Iterable[Record.RecordValue]]:
        for key in self.records.keys():
            if key.field == expression:
                return self.records[key]
            record_values = [rv for rv in self.records[key] if rv.expression == expression]
            if record_values:
                return record_values

        return None

    def __str__(self):
        return self.__repr__()

    def pause_record(self):
        self._should_record = False

    def resume_record(self):
        self._should_record = True
