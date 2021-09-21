from dataclasses import dataclass
from typing import Iterable, Callable, Collection

from tests.test_resources.oop_basic_java_2021.casa_de_burrito import CasaDeBurrito

class Professor(object):
    ...

@dataclass
class Professor(object):

    _id: int

    def favorite(self, c: CasaDeBurrito) -> Professor:
        pass

    def favorites(self) -> Collection[CasaDeBurrito]:
        pass

    def add_friend(self, p: Professor) -> Professor:
        pass

    @property
    def friends(self) -> set[Professor]:
        pass

    def filtered_friends(self, p: Callable) -> set[Professor]:
        pass

    def filter_and_sort_favorites(self, comp: Callable, p: Callable) -> Collection[CasaDeBurrito]:
        pass

    def favorites_by_rating(self, r_limit: int) -> Collection[CasaDeBurrito]:
        pass

    def __str__(self):
        pass

    @property
    def id(self):
        return self._id

    class SameProfessorException(Exception):
        pass

    class ProfessorAlreadyInSystemException(Exception):
        pass

    class ProfessorNotInSystemException(Exception):
        pass

    class UnratedFavoriteCasaDeBurritoException(Exception):
        pass

    class ConnectionAlreadyExistsException(Exception):
        pass