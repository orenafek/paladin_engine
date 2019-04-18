"""
    :file: archive.py
    :brief: A tracker of values of variables throughout the history of the program.
    :author: Oren Afek
    :since: 05/04/2019
"""


class Archive(object):
    """
        An archive of all values of variables throughout  the history of the program.
    """

    def __init__(self) -> None:
        """
            Constructor
        :param program: (ast.Node) A Node representing all
        """
        # Initialize the variables dict.
        self.vars_dict = {}

    def __setattr__(self, key, value):
