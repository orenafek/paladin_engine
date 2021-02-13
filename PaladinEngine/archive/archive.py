"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""
import inspect
from abc import abstractmethod, ABC
from enum import Enum
import ast
import re
from typing import Optional

import prettytable

from PaladinEngine.conf.engine_conf import ARCHIVE_PRETTY_TABLE_MAX_ROW_LENGTH


class Archive(object):
    class Record(ABC):
        ...

    class NamedRecord(Record):
        ...

    class AnonymousRecord(Record):
        ...

    class FunctionCallRecord(Record):
        ...

    class SubscriptRecord(Record):
        ...

    class __ModeOfSearch(Enum):
        ...

    ...


class Archive(object):
    """
        An archive of all values of variables throughout  the history of the program.
    """

    class EmptyFullNameException(Exception):
        pass

    class VariableNeverRecordedException(Exception):
        """
            Thrown upon an attempt of extracting the last value of
            a variable that has never been recorded.
        """

        def __init__(self, name):
            """
                Constructor.
            :param name: (str) The searched name.
            """
            super().__init__(name)

    class Record(ABC):
        """
            A record of a variable's value in a point in history.
        """

        class RecordValue(object):
            def __init__(self, value: object, line_no: int, time: int = -1):
                self._value = value
                self._line_no = line_no
                self._time = time

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, v):
                self._value = v

            @property
            def line_no(self):
                return self._line_no

            @line_no.setter
            def line_no(self, l_n):
                self._line_no = l_n

            @property
            def time(self):
                return self._time

            @time.setter
            def time(self, t):
                self._time = t

        def __init__(self, frame, value_type):
            """
                Constructor.
            :param time (int): The time of the record.
            :param value (object): The value of the variable.
            """

            # Set the frame.
            self.__frame = frame

            # Initialize the values list.
            self.__values = []

            # Set the type.
            self.__type = value_type

        @property
        def frame(self):
            return self.__frame

        @property
        def type(self):
            return self.__type

        @property
        def key(self):
            return Archive.Record.RecordKey(self.get_identifier(), self.frame)

        def __getitem__(self, time: int):
            """
                A getter for a specific value in time.
            :param time: (int) A specific time to retrieve a value of a record.
            :return: (object)
            """
            return self.__values[time]

        def __setitem__(self, time: int, new_value: object, line_no: int):
            """
                Set a new value in a specific time.
            :param time:  (int) A specific time.
            :param new_value: (object) A new value to store.
            """
            self.__values[time] = new_value

        @property
        def values(self) -> list:
            """
                A getter.
            :return: The values that were record.
            """
            return self.__values

        def get_last_value(self) -> object:
            """
                A getter that retrieves the last inserted value.
            :return:
            """
            return self.__values[::-1][0]

        def get_values_from_time(self, time: int) -> list:
            """
                Get the values of this record that were stored in a certain time, and beforehand.
            :param time: The time to filter from.
            :return:
            """
            return [record_value for record_value in self.values if record_value.time <= time]

        def get_last_value_from_time(self, time: int) -> tuple:
            """
                Get the last value of this record that was stored in a certain time, or beforehand.
            :param time: The time to filter from.
            :return: Either the last value (a tuple) or None.
            """
            return self.get_values_from_time(time)[::-1][0]

        def get_values_string(self):
            return Archive.Record.stringify(self.values)

        def store_value(self, record_value: RecordValue) -> Archive.Record:
            """
            Appends a value to the list of values of this record.
            :param value: A new value to store.
            :param line_no: The line number in which this value was stored.
            :param time: The time to store the value.
            :return:
            """
            self.__values.append(record_value)

            return self

        def __str__(self):
            """
                ToString.
            :return: (str)
            """
            return '{i}:{v}'.format(i=self.get_identifier(),
                                    v=[Archive.Record.stringify(v) for v in self.values])

        @abstractmethod
        def __eq__(self, other):
            raise NotImplementedError()

        @abstractmethod
        def __hash__(self):
            raise NotImplementedError()

        @abstractmethod
        def get_identifier(self):
            raise NotImplementedError()

        @staticmethod
        def stringify(obj):
            if isinstance(obj, list) or isinstance(obj, tuple):
                if len(obj) == 0:
                    return ''

                first_item = Archive.Record.stringify(obj[0])
                rest_of_iterable = Archive.Record.stringify(obj[1:])
                if rest_of_iterable == '':
                    return first_item

                return first_item + ", " + rest_of_iterable

            if isinstance(obj, dict):
                if len(obj) == 0:
                    return ''

                key = list(obj.keys())[0]
                value = obj.pop(key)
                return f'{Archive.Record.stringify(key)}: {Archive.Record.stringify(value)}' + \
                       Archive.Record.stringify(obj)

            return str(obj)

        class RecordKey(object):
            def __init__(self, identifier, frame):
                self.__identifier = identifier
                self.__frame = frame

            @property
            def identifier(self):
                return self.__identifier

            @property
            def frame(self):
                return self.__frame

            def __eq__(self, other):
                return isinstance(other, Archive.Record.RecordKey) \
                       and other.identifier == self.identifier \
                       and other.frame is self.frame

            def __hash__(self):
                return hash(hash(self.identifier) + hash(self.frame))

            def __repr__(self) -> str:
                return f"({self.identifier}, {self.frame})"

        @abstractmethod
        def is_string_of_type(self, string: str) -> bool:
            raise NotImplementedError

        @classmethod
        def expression_matches(cls, expression: str) -> bool:
            return True

    class AnonymousRecord(Record):
        """
            An anonymous record, identified by the python built-in id.
        """

        def __init__(self, id, frame, value_type):
            super().__init__(frame, value_type)

            # Set the id.
            self.__id = id

        def __eq__(self, other):
            """
                An equality tester.
                One NamedRecord equals to another iff their id is equal.
            :param other: (obj) Another object.
            :return: True <==> self == other, False otherwise.
            """
            # Test the type of the other object.
            if not isinstance(other, Archive.AnonymousRecord):
                return False

            # Find equality by the id.
            return self.__id == other.__id

        def __hash__(self):
            return hash(self.__id)

        def get_identifier(self):
            return self.__id

        @classmethod
        def expression_matches(cls, expression: str) -> bool:
            return re.match(f'(((\s*[A-Za-z_]\w*\s*)(.)+)(\s*[A-Za-z_]\w*\s*))', expression) is not None

    class NamedRecord(Record):
        """
            A Named record tracks an object with a given variable name.
        """

        def __init__(self, name, frame, value_type):
            # Initialize parent.
            super().__init__(frame, value_type)

            # Set the name.
            self.__name = name

        def __eq__(self, other):
            """
                An equality tester.
                One NamedRecord equals to another iff their name is equal.
            :param other: (obj) Another object.
            :return: True <==> self == other, False otherwise.
            """
            # Test the type of the other object.
            if not isinstance(other, Archive.NamedRecord):
                return False

            return self.__name == other.__name

        def __hash__(self):
            return hash(self.__name)

        def __str__(self):
            return f'{self.__name}:{str(super())}'

        def get_identifier(self):
            return self.__name

        @classmethod
        def expression_matches(cls, expression: str) -> bool:
            return re.match('^[^.]+$', expression) is not None

    class FunctionCallRecord(Record):
        """
            A record that tracks function calls.
        """

        def __init__(self, name, frame, value_type):
            # Initialize parent.
            super().__init__(frame, value_type)

            # Set the name.
            self.__name = name

        def __eq__(self, other):
            """
                An equality tester.
                One NamedRecord equals to another iff their name is equal.
            :param other: (obj) Another object.
            :return: True <==> self == other, False otherwise.
            """
            # Test the type of the other object.
            if not isinstance(other, Archive.FunctionCallRecord):
                return False

            return self.__name == other.__name

        def __hash__(self):
            return hash(self.__name)

        def __str__(self):
            return f'{self.__name}:{str(super())}'

        def get_identifier(self):
            return self.__name

        def store_value(self, args_kwargs: list, value: object, line_no: int, time: int) -> Archive.FunctionCallRecord:
            """
            Appends a value to the list of values of this record.
            :param args_kwargs: List of args and kwargs.
            :param value: A new value to store.
            :param line_no: The line number in which this value was stored.
            :param time: The time to store the value.
            :return:
            """
            self.__values.append((value, line_no, time))
            return self

        @classmethod
        def expression_matches(cls, expression: str) -> bool:
            # The string has a ().
            class FunctionVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.counter = 0

                def visit_Call(self, node):
                    self.counter += 1

            visitor = FunctionVisitor()
            visitor.visit(ast.parse(expression))
            return visitor.counter > 0

    class SubscriptRecord(NamedRecord):

        def __init__(self, name, frame, value, _slice, line_no, time=0):
            super().__init__(name, frame, value, line_no, time)

            # Set slice.
            self.__slice = _slice

        def __eq__(self, other):
            return super().__eq__(other) and self.slice == other.slice

        def __hash__(self):
            return hash(hash(super) + hash(self.__slice))

        @property
        def slice(self):
            return self.__slice

        @classmethod
        def expression_matches(cls, expression: str) -> bool:
            return re.match('[A-Za-z$_]+[A-Za-z$_0-9\-]*\[[A-Za-z$_0-9,:\-]*\]', expression) is not None

    def __init__(self) -> None:
        """
            Constructor
        """
        # Initialize the variables dict.
        self.records = {}

        # Initialize the variables dict.
        self.__named_records = {}

        # Initialize the anonymous dict.
        self.__anonymous_records = {}

        # Initialize the commitments dict.
        self._commitments = {}

        # Initialize the global time counter.
        self._global_time_counter = 0

    @property
    def last_time_counter(self):
        return self._global_time_counter

    def _advance_time_counter(self) -> Archive:
        self._global_time_counter += 1

        return self

    def history(self, var) -> list:
        """
            Extract all history of a variable.
        :param var: (str) The name of a variable.
        :return: (list[Record]) The history of the variable.
        """
        # Check if the var has been recorded yet:
        if var not in self.__named_records:
            raise Archive.VariableNeverRecordedException(var)

        return self.__named_records[var]

    def values(self, var) -> list:
        """
            Extract all of the values of a variable through out history.
        :param var: (str) The name of a variable.
        :return: (list) All of the values of the variable.
        """
        return self.history(var)

    def all_history(self) -> dict:
        """
            Extract all of the history of all of the variables in the archive.
        :return: (dict[str, list[Record]]) A mapping between a var and its records through out history.
        """

        return self.vars_dict

    def all_records(self) -> dict:
        all_records = {}
        all_records.update(self.__named_records)
        all_records.update(self.__anonymous_records)
        return all_records

    def __str__(self):
        """
            Returns a string representing the archive.
            For each var, a list of strings representing the values of the var throughout its history.
        :return:
        """

        # Create a pretty table.
        table = prettytable.PrettyTable(border=prettytable.ALL,
                                        hrules=1,
                                        field_names=['variable', 'values'])
        table.align = 'l'
        table.max_width = ARCHIVE_PRETTY_TABLE_MAX_ROW_LENGTH

        all_records = self.all_records()

        # Add rows from the archive.

        for record in all_records.values():
            table.add_row([record.get_identifier(), [record.get_values_string()]])

        return table.get_string()

    def vars(self) -> list:
        """
            Extract all of the variables that has been recorded in the archive.
        :return: (list) All of the variables.
        """
        return list(self.vars_dict.keys())

    def __search_by_id(self, _id):
        """
            Searches for an object in the archive by an id.
        :param _id: (int) An id.
        :return: a Record in case one exist with that id, None otherwise.
        """
        # Search in anonymous records.
        try:
            return self.__anonymous_records[_id]
        except KeyError:
            # The id is not in the anonymous records, therefore search for it in the named records.
            for record in self.__named_records:
                if record.id == _id:
                    return record

        # The id didn't match any stored record, therefore leave empty handed.
        return None

    class __ModeOfSearch(Enum):
        CREATE_IF_MISSING = 1,
        THROW_IF_MISSING = 2

    def __name_to_record_type(self, full_name: str) -> type:
        for subclass in Archive.Record.__subclasses__():
            if subclass.is_string_of_type(full_name):
                return subclass

        return type(None)

    def __search3(self, expression: str, vars_dict: dict, value: Record.RecordValue, frame=None) -> Optional[Archive.Record]:

        # Check if the expression is simply a var (should be of type "NamedRecord")
        if Archive.NamedRecord.expression_matches(expression):



    def __search2(self, expression: str, vars_dict: dict, frame=None) -> Optional[Archive.Record]:
        pass

    def __search_record(self, full_name: str, vars_dict: dict, frame=None) -> Optional[Archive.Record]:

        # Search for the record type.
        record_type = self.__name_to_record_type(full_name)

        if record_type is None:
            return None

        if record_type is Archive.NamedRecord:
            name = full_name.split('.')[0]
            if frame is None:
                for key in self.__named_records:
                    if key.identifier == name:
                        named_record_key = key
                        break
                if named_record_key is None:
                    return None
            else:
                named_record_key = Archive.NamedRecord.RecordKey(name, frame)

            record = self.__named_records[named_record_key]

        elif record_type is Archive.AnonymousRecord:
            named_record_identifier = full_name.split(Archive.AnonymousRecordsIterator.COMPONENT_SEPARATOR)[0]
            for anonymous_value in \
                    Archive.AnonymousRecordsIterator(full_name, self.__find_symbol_in_vars_dict(vars_dict,
                                                                                                named_record_identifier)):
                record = self.__anonymous_records[id(anonymous_value)]

        elif record_type is Archive.FunctionCallRecord:

        return record

    def __search_record_and_store_value(self, full_name: str, vars_dict: dict,
                                        mode_of_search: Archive.__ModeOfSearch, record_value: Record.RecordValue = None,
                                        frame: dict = None,
                                        line_no: int = -1) -> Record:
        """
            Searches for an object in the archive by a full name.
            A 'Full Name' contains a series of references leading to the searched object.
            e.g.: 'x.y.z'

        :param value:
        :param full_name: (str) A 'Full Name'
        :param vars_dict: (dict) A dictionary with all vars to look in.
        :param time_of_search: (int) The time of the value to search.
                                (-1): To search for the last value of the record.
        :return: The searched record or None if such doesn't exist.
        """

        # If the full name is empty, leave.
        if full_name == '':
            raise Archive.EmptyFullNameException()

        record = self.__search_or_create_named_record(frame, mode_of_search, full_name, line_no, vars_dict,
                                                      record_value)

        if len(full_name.split('.')) > 1:
            for anonymous_value in Archive.AnonymousRecordsIterator(full_name, record.get_last_value()):
                anonymous_id = id(anonymous_value)

                # Retrieve the record from the archive.
                try:
                    record = self.__anonymous_records[anonymous_id]
                except KeyError:
                    # There is no suitable anonymous record for this component, create one.
                    record = Archive.AnonymousRecord(anonymous_id, frame, type(anonymous_value))

                    # Create a new record value object.
                    record_value_class = type(record_value)
                    new_record_value = record_value_class(anonymous_value, line_no, self.last_time_counter)
                    record.store_value(new_record_value)

                    # Store it in the anonymous records table.
                    self.__anonymous_records[anonymous_id] = record

        # Return the value of the last component found.
        return record

    class AnonymousRecordsIterator(object):
        COMPONENT_SEPARATOR = '.'

        def __init__(self, full_name: str, named_component_value: object):
            self._full_name = full_name
            self._named_component_value = named_component_value
            self._current_component_value = None

        def __iter__(self):
            try:
                self._split_to_components(self._full_name)
                self._current_component_value = self._named_component_value
            except IndexError:
                raise StopIteration()

            return self

        def __next__(self):
            try:
                self._current_component_value = self._current_component_value.__getattribute__(
                    self.other_components.pop(0))
            except IndexError:
                raise StopIteration

            return self._current_component_value

        def _split_to_components(self, full_name: str):
            # Split to components.
            all_components = full_name.split(Archive.AnonymousRecordsIterator.COMPONENT_SEPARATOR)

            # Store the named component.
            self.named_component = all_components[0]

            # Store the fields.
            self.other_components = all_components[1::]

    def __search_or_create_named_record(self, frame: dict, mode_of_search, full_name: str, line_no: int,
                                        vars_dict: dict, record_value: Record.RecordValue):

        # Split the full name to its components.
        name = full_name.split('.')[0]

        # Initiate.
        named_record_key = None

        # If there is a frame, search for a specific record.
        if frame is not None:
            # Create a NamedRecordKey.
            named_record_key = Archive.NamedRecord.RecordKey(name, frame)
        else:
            for key in self.__named_records:
                if key.identifier == name:
                    named_record_key = key

        # Create a named record
        # Fetch the value of the name from the vars dict.
        value = self.__find_symbol_in_vars_dict(vars_dict, name)

        # Search for the named record.
        if named_record_key not in self.__named_records:
            # If the value is none, we're in retrieve mode, therefore leave empty handed.
            if mode_of_search is Archive.__ModeOfSearch.THROW_IF_MISSING:
                raise Archive.VariableNeverRecordedException(name)

            # Create a named record.
            named_record = Archive.NamedRecord(name, frame, type(value))

            # Store it in the named records map.
            self.__named_records[named_record.key] = named_record

            named_record_key = named_record.key

        # Store the named record's value.
        if record_value is None:
            record_value = Archive.Record.RecordValue(value, line_no, self.last_time_counter)
        else:
            record_value.value = value
            record_value.line_no = line_no,
            record_value.time = self.last_time_counter

        # Initiate a pointer to the record.
        record = self.__named_records[named_record_key]

        record.store_value(record_value)

        return record

    def retrieve(self, full_name: str, vars_dict: dict = None) -> Archive.Record:
        """
            Searches for an object in the archive by a full name.
            A 'Full Name' contains a series of references leading to the searched object.
            e.g.: 'x.y.z'

        :param full_name: (str) A 'Full Name'
        :param vars_dict: (dict) The dict containing the named variables.
        :return: The searched record or None if such doesn't exist.
        """
        if vars_dict is None:
            vars_dict = Archive.__retrieve_callee_locals_and_globals()

        # Search for the record.
        return self.__search_record(full_name, vars_dict)
        # return self.__search_record_and_store_value(full_name, vars_dict, Archive.__ModeOfSearch.THROW_IF_MISSING)

    def store(self, full_name: str, frame: dict, line_no: int, record_value: Record.RecordValue = None,
              vars_dict: dict = None) -> Archive:
        """
            Stores a new object in the archive.
        :param full_name: The full name fo the object to store.
        :param value: A new value to store.
        :param line_no: The line number that triggered the store in the archive.
        :param frame: The frame of the code section that trigger the store in the archive.
        :param vars_dict: The dict containing the named variables.
        :return: self.
        """

        if vars_dict is None:
            vars_dict = Archive.__retrieve_callee_locals_and_globals()

        # Search for the record and store.
        record = self.__search_record_and_store_value(full_name, vars_dict, Archive.__ModeOfSearch.CREATE_IF_MISSING,
                                                      record_value, frame, line_no)

        # Advance the time.
        self._advance_time_counter()

        # Validate commitments.
        # if record.frame is frame:
        self._validate_commitments(record, line_no)

        return self

    @staticmethod
    def __retrieve_callee_locals_and_globals():
        """
            Retrieve all locals and globals variables of the callee of this function
        :return:
        """
        # Get callee frame.
        frame = inspect.currentframe().f_back.f_back

        # Create a dict for all the variables.
        all_vars = {}

        # Add the locals.
        all_vars = frame.f_locals

        # Add the globals.
        all_vars.update(frame.f_globals)

        return all_vars

    def __find_symbol_in_vars_dict(self, vars_dict: dict, name: str):
        if name in vars_dict:
            return vars_dict[name]

        for var in vars_dict:
            # TODO: COMPLETE INNER SEARCH INSIDE EACH VAR.
            pass

        return None

    def clear(self):
        # Clear named records.
        self.__named_records.clear()

        # Clear anonymous records.
        self.__anonymous_records.clear()

    def make_commitment(self, name: str, frame: dict, commitment, vars_dict: dict = None) -> Archive:
        """
            Make a commitment that should satisfy a record throughout the run.
        :param record: A record to commit.
        :param commitment: A commitment about the record
        :return: self
        """
        # Find the record.
        record = self.__search_record_and_store_value(name, vars_dict,
                                                      Archive.__ModeOfSearch.CREATE_IF_MISSING, frame)
        # Create key.
        record_key = record.key

        if record_key not in self._commitments.keys():
            self._commitments[record_key] = [commitment]
        else:
            self._commitments[record_key].append(commitment)
        return self

    def _validate_commitments(self, record: Archive.Record, line_no):
        """
            Validate that all commitments are satisfied.
        :param record: A record to validate
        :return:
        """
        # if self._commitments == {} or record.key not in self._commitments:
        #    return

        # If there are no commitments, leave.
        if self._commitments == {}:
            return

        def try_to_locate_object_in_frame(object_id, frame):
            for local in frame.f_locals.values:
                # Look for the local itself.
                if id(local) is object_id:
                    return local

                # Go over the attributes of the local.
                for attr in local.__dict__.values:
                    if id(attr) == object_id:
                        return attr

            return None

        def is_key_match(commitment_record_key: Archive.Record.RecordKey) -> bool:
            # # Filter the keys that match the same identifier.
            # matching_identifiers = record.key.frame.f_locals.keys() & commitment_record_key.frame.f_locals.keys()
            #
            # if isinstance(record, Archive.NamedRecord) and record.key.identifier in record.key.frame.f_locals or\
            #         isinstance(record, Archive.AnonymousRecord) and \
            #         record.key.identifier in [id(record.key.frame.f_locals[local]) for local in record.key.frame.f_locals]:
            #     matching_types = type(record.key.frame.f_locals[record.key.identifier]) is \
            #                      type(commitment_record_key.frame.f_locals[commitment_record_key.identifier])
            #
            #     return len(matching_identifiers) > 0 and matching_types

            return record.key.identifier == commitment_record_key.identifier
            # return try_to_locate_object_in_frame(record.key.identifier, commitment_record_key.frame) is not None

        # Filter the commitments by the record's type.
        # TODO: This is a patch and should be rethought in the future.
        for _, commitments in {k: v for k, v in self._commitments.items() if is_key_match(k)}.items():
            for c in commitments:
                c(record, line_no)

    def _has_commitments(self):
        return len(self._commitments.keys()) > 0
