from TemporalParser.building_blocks.abstract.collectible import Collectible


class Event(Collectible):
    def __init__(self, *args):
        super().__init__()
        self.__inner_call = None

    def collect(self, stack: list):
        return super().collect(stack)


class ImmediateEvent(Event):

    def __init__(self, *args):
        super().__init__(*args)


class CallEvent(Event):
    def __init__(self, *args):
        super().__init__(*args)
        self.__call = None

    def collect(self, stack: list):
        self.__call = stack.pop()
        return stack


class ChangeDataEvent(Event):
    def __init__(self, *args):
        super().__init__(*args)
        self.__change_data = None
