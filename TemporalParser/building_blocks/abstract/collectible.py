from abc import ABC, abstractmethod


class Collectible(ABC):
    def __init__(self):
        super().__init__()
        self.__value = None

    @abstractmethod
    def collect(self, stack: list):
        return stack
