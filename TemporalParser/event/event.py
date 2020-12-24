from TemporalParser.building_blocks.abstract.collectible import Collectible


class Event(Collectible):
    def __init__(self, *args):
        super().__init__()
        self.__cause = None

    @property
    def cause(self):
        return self.__cause

    @cause.setter
    def cause(self, value):
        self.__cause = value

    def collect(self, stack: list):
        # Extract cause from stack.
        self.cause = stack.pop()

        return stack
