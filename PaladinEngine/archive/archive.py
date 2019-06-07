"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""
import copy

import prettytable

from conf.engine_conf import ARCHIVE_PRETTY_TABLE_MAX_ROW_LENGTH


class Archive(object):
    """
        An archive of all values of variables throughout  the history of the program.
    """

    class VariableNeverRecordedException(Exception):
        """
            Thrown upon an attempt of extracting the last value of
            a variable that has never been recorded.
        """
        pass

    class Var(object):
        """
            A variable that is stored in the archive.
        """

        def __init__(self, var_id, var_name):
            """
                Constructor.
            :param var_id: (int) The pythonic identification number of the variable.
            :param var_name: (str) The name of the variable.
            """
            self.var_id = var_id
            self.var_name = var_name

        def __hash__(self):
            return self.var_id.__hash__()

        def __eq__(self, other):
            return isinstance(other, Archive.Var) and other.var_id == self.var_id

        def __ne__(self, other):
            return not (self == other)

        def __cmp__(self, other):
            if not isinstance(other, Archive.Var):
                return 1
            else:
                return self.var_id.__cmp__(other.var_id)

    class Record(object):
        """
            A record of a variable's value in a point in history.
        """

        def __init__(self, time, value):
            """
                Constructor.
            :param time (int): The time of the record.
            :param value (object): The value of the variable.
            """
            # Set the time.
            self.__time = time

            # Set the value.
            self.__value = value

        def time(self) -> int:
            """
                Getter.
            :return: (int) The time that the record was taken.
            """
            return self.__time

        def value(self) -> object:
            """
                Getter.
            :return: The value that was record.
            """
            return self.__value

        def __str__(self):
            """
                ToString.
            :return: (str)
            """
            return '{t}:{v}'.format(t=self.time(), v=self.value())

    def __init__(self) -> None:
        """
            Constructor
        """
        # Initialize the variables dict.
        self.vars_dict = {}

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

    def __setitem__(self, var_id, var_name, value):
        """
            Record a new value of a variable.
        :param var_id (id) The id of the variable to record its new value.
        :param var_name (str) The name of the variable to record its new value.
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
        record = Archive.Record(time, cloned_value)

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
        return [record.value() for record in self.history(var)]

    def all_history(self) -> dict:
        """
            Extract all of the history of all of the variables in the archive.
        :return: (dict[str, list[Record]]) A mapping between a var and its records through out history.
        """

        return self.vars_dict

    def all_values(self) -> dict:
        """
            Extract all of the values of all of the variables in the archive.
        :return: (dict[str, list[Record]]) A mapping between a var and its values through out history.
        """

        return {var: self.values(var) for var in self.vars_dict.keys()}

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

        # Add rows from the archive.
        for var, values in self.all_values().items():
            table.add_row([var, ', '.join(str(v) for v in values)])

        return table.get_string()

    def vars(self) -> list:
        """
            Extract all of the variables that has been recorded in the archive.
        :return: (list) All of the variables.
        """
        return list(self.vars_dict.keys())
