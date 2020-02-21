from TemporalParser.building_blocks.abstract.keyword import Keyword


class Condition(Keyword):
    def __init__(self, literal, case=None):
        super().__init__(literal, case)
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


always = Condition("always")
eventually = Condition("eventually")
never = Condition("never")
