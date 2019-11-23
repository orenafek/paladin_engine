"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""
import copy
import inspect
from abc import abstractmethod, ABC
from enum import Enum

import prettytable

from PaladinEngine.conf.engine_conf import ARCHIVE_PRETTY_TABLE_MAX_ROW_LENGTH


class Archive(object):
    class VariableNeverRecordedException(Exception):
        ...

    class Record(ABC):
        ...

    class NamedRecord(Record):
        ...

    class AnonymousRecord(Record):
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

        def __init__(self, value, time):
            """
                Constructor.
            :param time (int): The time of the record.
            :param value (object): The value of the variable.
            """
            # Set the time.
            self.__time = time

            # Initialize the values list.
            self.__values = [value]

        def time(self) -> int:
            """
                Getter.
            :return: (int) The time that the record was taken.
            """
            return self.__time

        def __getitem__(self, time: int):
            """
                A getter for a specific value in time.
            :param time: (int) A specific time to retrieve a value of a record.
            :return: (object)
            """
            return self.__values[time]

        def __setitem__(self, time: int, new_value: object):
            """
                Set a new value in a specific time.
            :param time:  (int) A specific time.
            :param new_value: (object) A new value to store.
            """
            self.__values[time] = new_value

        def get_values(self) -> object:
            """
                A getter.
            :return: The values that were record.
            """
            return self.__values

        def append(self, value: object) -> Archive.Record:
            """
                Appends a value to the list of values of this record.
            :param value: (object) A new value to store.
            :return: self.
            """
            self.__values.append(value)

            return self

        def __str__(self):
            """
                ToString.
            :return: (str)
            """
            return '{i}:{t}:{v}'.format(i=self.get_identifier(), t=self.time(), v=self.get_values())

        @abstractmethod
        def __eq__(self, other):
            raise NotImplementedError()

        @abstractmethod
        def get_identifier(self):
            raise NotImplementedError()

    class AnonymousRecord(Record):
        """
            An anonymous record, identified by the python built-in id.
        """

        def __init__(self, id, value, time=0):
            super().__init__(value, time)

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

        def get_identifier(self):
            return self.__id

    class NamedRecord(Record):
        """
            A Named record tracks an object with a given variable name.
        """

        def __init__(self, name, value, time=0):
            # Initialize parent.
            super().__init__(value, time)

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

        def __str__(self):
            return '{n}:{rest}'.format(n=self.__name, rest=super().__str__())

        def get_identifier(self):
            return self.__name

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

    def __getitem__(self, var) -> Record:
        """
            Retrieve the last value of of a variable.
        :param var (str) The name of the variable to retrieve its value.
        :return: The last value of the variable.
        """
        # Check if the var has been recorded yet:
        if var not in self.vars_dict:
            raise Archive.VariableNeverRecordedException(var)

        # Extract record list.
        records = self.vars_dict[var]

        # Extract last value.
        return records[0]

    def __setitem__(self, var, value):
        """
            Record a new value of a variable.
        :param var (str) The name of the variable to record its new value.
        :param value (object) The value to record.
        """
        # Check if the var has been recorded yet:
        if var not in self.vars_dict:
            self.vars_dict[var] = []

        # Extract record list.
        records = self.vars_dict[var]

        # Set the time.
        if not records:
            time = 0
        else:
            time = records[0].time() + 1

        # Clone the value.
        cloned_value = copy.deepcopy(value)

        # Create a record.
        record = Archive.Record(cloned_value)

        # Save the new record.
        records.insert(0, record)

    def history(self, var) -> list:
        """
            Extract all history of a variable.
        :param var: (str) The name of a variable.
        :return: (list[Record]) The history of the variable.
        """
        # Check if the var has been recorded yet:
        if var not in self.vars_dict:
            raise Archive.VariableNeverRecordedException(var)

        return self.vars_dict[var]

    def values(self, var) -> list:
        """
            Extract all of the values of a variable through out history.
        :param var: (str) The name of a variable.
        :return: (list) All of the values of the variable.
        """
        return [record.get_values() for record in self.history(var)]

    def all_history(self) -> dict:
        """
            Extract all of the history of all of the variables in the archive.
        :return: (dict[str, list[Record]]) A mapping between a var and its records through out history.
        """

        return self.vars_dict

    def __all_records(self) -> dict:
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

        all_records = self.__all_records()

        # Add rows from the archive.
        for record in all_records.values():
            table.add_row([record.get_identifier(), record.get_values()])

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

    def __search_by_full_name_and_create_missing(self, full_name: str, vars_dict: dict,
                                                 mode_of_search: Archive.__ModeOfSearch,
                                                 time_of_search: int = -1) -> Record:
        """
            Searches for an object in the archive by a full name.
            A 'Full Name' contains a series of references leading to the searched object.
            e.g.: 'x.y.z'

        :param full_name: (str) A 'Full Name'
        :param vars_dict: (dict) A dictionary with all vars to look in.
        :param time_of_search: (int) The time of the value to search.
                                (-1): To search for the last value of the record.
        :return: The searched record or None if such doesn't exist.
        """

        # If the full name is empty, leave.
        if full_name == '':
            raise Archive.EmptyFullNameException()

        # Split the full name to its components.
        components = full_name.split('.')

        # Extract the name.
        name = components[0]

        if name not in self.__named_records:
            # If the value is none, we're in retrieve mode, therefore leave empty handed.
            if mode_of_search is Archive.__ModeOfSearch.THROW_IF_MISSING:
                raise Archive.VariableNeverRecordedException(full_name)

            # Fetch the value of the name from the vars dict.
            value = vars_dict[name]

            # Create a named record.
            named_record = Archive.NamedRecord(name, value)

            # Store it in the named records map.
            self.__named_records[name] = named_record

        # Initiate a pointer to the record.
        record = self.__named_records[name]

        # Fetch all components values.
        component_values = record.get_values()

        # Fetch the component's value.
        if time_of_search == -1:
            component_value = component_values[::-1][0]
        else:
            component_value = component_values[time_of_search]

        next_component_value = component_value

        for component in components[1::]:
            # Search for the next component's id.
            next_component_value = component_value.__getattribute__(component)

            next_component_id = id(next_component_value)

            # Retrieve the record from the archive.
            try:
                record = self.__anonymous_records[next_component_id]
            except KeyError:
                # There is no suitable anonymous record for this component, create one.
                record = Archive.AnonymousRecord(next_component_id, next_component_value)

                # Store it in the anonymous records table.
                self.__anonymous_records[next_component_id] = record

        if mode_of_search is Archive.__ModeOfSearch.CREATE_IF_MISSING:
            # Update the record's value.
            record.append(next_component_value)

        # Return the value of the last component found.
        return record

    def retrieve(self, full_name: str, vars_dict: dict = None) -> object:
        """
            Searches for an object in the archive by a full name.
            A 'Full Name' contains a series of references leading to the searched object.
            e.g.: 'x.y.z'

        :param full_name: (str) A 'Full Name'
        :return: The searched record or None if such doesn't exist.
        """
        if vars_dict is None:
            vars_dict = Archive.__retrieve_callee_locals_and_globals()

        # Search for the record.
        record = self.__search_by_full_name_and_create_missing(full_name, vars_dict,
                                                               Archive.__ModeOfSearch.THROW_IF_MISSING)
        if record is None:
            return record

        return record.get_values()

    def store(self, full_name: str, vars_dict: dict = None) -> Archive:
        """
            Stores a new object in the archive.
        :param full_name: (str) The full name fo the object to store.
        :param vars_dict: (dict) The dict containing the named variables.
        :return: self.
        """

        if vars_dict is None:
            vars_dict = Archive.__retrieve_callee_locals_and_globals()

        # Search for the record.
        record = self.__search_by_full_name_and_create_missing(full_name, vars_dict,
                                                               Archive.__ModeOfSearch.CREATE_IF_MISSING)

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

    def clear(self):
        # Clear named records.
        self.__named_records.clear()

        # Clear anonymous records.
        self.__anonymous_records.clear()
