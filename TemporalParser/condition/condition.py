from TemporalParser.building_blocks.abstract.collectible import Collectible


class Condition(Collectible):
    def __init__(self, *args):
        super().__init__()
        self.__condition = None

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, value):
        self.__condition = value

    def collect(self, stack: list) -> list:
        self.condition = stack.pop()
        return stack