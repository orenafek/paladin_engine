from dataclasses import dataclass

from tests.test_resources.oop_basic_java_2021.professor import Professor


class CasaDeBurrito(object):
    ...


@dataclass
class CasaDeBurrito(object):
    _id: int
    _name: str
    _distance: int
    _menu: set[str]

    def is_rated_by(self, p: Professor) -> bool:
        pass

    def rate(self, p: Professor, r: int) -> CasaDeBurrito:
        pass

    def number_of_rates(self) -> int:
        pass

    def average_rating(self) -> float:
        pass

    def __str__(self) -> str:
        pass

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def distance(self):
        return self._distance

    class CasaDeBurritoAlreadyInSystemException(Exception):
        pass

    class CasaDeBurritoNotInSystemException(Exception):
        pass

    class RateRangeException(Exception):
        pass
