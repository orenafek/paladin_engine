import sys
from dataclasses import dataclass, field
from typing import Callable
from typing import Collection, Dict, List

import networkx as nx

from tests.test_resources.oop_basic_java_2021.abstract.abstract import *


@dataclass
class Professor(object):
    _id: int
    _name: str
    _favorites: set = field(default_factory=set)
    _friends: set = field(default_factory=set)

    def favorite(self, c: CasaDeBurrito) -> Professor:
        if not c.is_rated_by(self):
            raise Professor.UnratedFavoriteCasaDeBurritoException()

        self._favorites.add(c)

        return self

    @property
    def favorites(self) -> Collection[CasaDeBurrito]:
        return self._favorites.copy()

    def add_friend(self, p: Professor) -> Professor:
        if p == self:
            raise Professor.SameProfessorException()

        if p in self._friends:
            raise Professor.ConnectionAlreadyExistsException()

        return self

    @property
    def friends(self) -> set[Professor]:
        return self._friends.copy()

    def filtered_friends(self, p: Callable) -> set[Professor]:
        return set([f for f in self._friends if p(f)])

    def filter_and_sort_favorites(self, comp: Callable, p: Callable) -> Collection[CasaDeBurrito]:
        return sorted([c for c in self.favorites if p(c)], key=comp)

    def favorites_by_rating(self, r_limit: int) -> Collection[CasaDeBurrito]:
        return self.filter_and_sort_favorites(p=lambda c: c.average_rating() >= r_limit,
                                              comp=lambda c: (c.average_rating, c.distance, c.id))

    def favorites_by_dist(self, d: int) -> Collection[CasaDeBurrito]:
        return self.filter_and_sort_favorites(p=lambda c: c.distance <= d,
                                              comp=lambda c: (c.distance, c.average_rating, c.id))

    def __str__(self):
        return f'Professor: {self._name}\nId: {self.id}\nFavorites: {[c.name for c in self._favorites]}'

    def __eq__(self, other):
        return isinstance(other, Professor) and self.id == other.id

    def __ge__(self, other):
        if not isinstance(other, Professor):
            raise RuntimeError(f'Trying to sort A Professor and a {type(other).__name__}.')

        return self.id > other.id

    def __le__(self, other):
        return not self > other and not self == other

    @property
    def id(self):
        return self._id

    class SameProfessorException(BaseException):
        pass

    class ProfessorAlreadyInSystemException(BaseException):
        pass

    class ProfessorNotInSystemException(BaseException):
        pass

    class UnratedFavoriteCasaDeBurritoException(BaseException):
        pass

    class ConnectionAlreadyExistsException(BaseException):
        pass
