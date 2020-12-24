from TemporalParser.building_blocks.abstract.collectible import Collectible


class Phrase(Collectible):
    def __init__(self, *args):
        super().__init__()
        self.__inner_phrase = None

    @property
    def inner_phrase(self):
        return self.__inner_phrase

    @inner_phrase.setter
    def inner_phrase(self, value):
        self.__inner_phrase = value

    def collect(self, stack: list):
        # Extract inner phrase.
        self.__inner_phrase = stack.pop()

        return stack


class SimplePhrase(Phrase):
    def __init__(self, *args):
        super().__init__(*args)
        self.__event = None

    @property
    def event(self):
        return self.__event

    @event.setter
    def event(self, v):
        self.__event = v

    def collect(self, stack: list):
        self.event = stack.pop()
        return stack


class ComplexPhrase(Phrase):
    def __init__(self, *args):
        super().__init__(*args)
        self.__time_connector = None
        self.__event = None
        self.__condition = None
        self.__phrase = None

    def collect(self, stack: list):
        # Extract phrase.
        self.phrase = stack.pop()

        # Extract condition.
        self.condition = stack.pop()

        # Extract event.
        self.event = stack.pop()

        # Extract time-connector.
        self.time_connector = stack.pop()

        return stack

    @property
    def time_connector(self):
        return self.__time_connector

    @time_connector.setter
    def time_connector(self, v):
        self.__time_connector = v

    @property
    def event(self):
        return self.__event

    @event.setter
    def event(self, v):
        self.__event = v

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, v):
        self.__condition = v

    @property
    def phrase(self):
        return self.__phrase

    @phrase.setter
    def phrase(self, v):
        self.__phrase = v
