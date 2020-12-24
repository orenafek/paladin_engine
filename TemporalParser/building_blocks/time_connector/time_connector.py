from TemporalParser.building_blocks.abstract.collectible import Collectible


class TimeConnector(Collectible):
    def __init__(self, *args):
        super().__init__()
        self.__time_connector = None

    @property
    def time_connector(self):
        return self.__time_connector

    @time_connector.setter
    def time_connector(self, value):
        self.__time_connector = value

    def collect(self, stack: list):
        self.time_connector = stack.pop()
        return stack
