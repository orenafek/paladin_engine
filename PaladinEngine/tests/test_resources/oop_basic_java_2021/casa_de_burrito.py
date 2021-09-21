from dataclasses import dataclass, field
from typing import List

from tests.test_resources.oop_basic_java_2021.professor import Professor


class CasaDeBurrito(object):
    ...


@dataclass
class CasaDeBurrito(object):
    _id: int
    _name: str
    _distance: int
    _menu: set[str]
    _rates: dict = field(default_factory=lambda: [])

    def is_rated_by(self, p: Professor) -> bool:
        return p in self._rates

    def rate(self, p: Professor, r: int) -> CasaDeBurrito:
        if r < 0 or r > 5:
            raise CasaDeBurrito.RateRangeException()

        self._rates[p] = r

        return self

    def number_of_rates(self) -> int:
        return len(self._rates)

    def average_rating(self) -> float:
        return sum(self._rates.values()) / len(self._rates)

    def __str__(self) -> str:
        return f'CasaDeBurrito: {self.name}\nId: {self.id}\nDistance: {self._distance}\nMenu: {self._menu}'

    def __eq__(self, o: object) -> bool:
        return isinstance(o, CasaDeBurrito) and o.id == self.id

    def __ge__(self, other):
        if not isinstance(other, CasaDeBurrito):
            raise RuntimeError(f'Trying to sort A CasaDeBurrito and a {type(other).__name__}.')

        return self.id > other.id

    def __le__(self, other):
        return not self > other and not self == other

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
