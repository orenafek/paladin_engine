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

    def __hash__(self):
        return hash(self.id)
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


@dataclass
class CasaDeBurrito(object):
    _id: int
    _name: str
    _distance: int
    _menu: set[str]
    _rates: Dict = field(default_factory=lambda: {})

    def is_rated_by(self, p: Professor) -> bool:
        return p in self._rates

    def rate(self, p: Professor, r: int) -> CasaDeBurrito:
        if r < 0 or r > 5:
            raise CasaDeBurrito.RateRangeException()

        self._rates[p.id] = r

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

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def distance(self):
        return self._distance

    class CasaDeBurritoAlreadyInSystemException(BaseException):
        pass

    class CasaDeBurritoNotInSystemException(BaseException):
        pass

    class RateRangeException(BaseException):
        pass


class CartelDeNachos(object):

    def __init__(self):
        self._professors: Dict[int, Professor] = {}
        self._casas_de_burrito: Dict[int, CasaDeBurrito] = {}

    def join_cartel(self, professor_id: int, professor_name: str) -> Professor:
        p = Professor(professor_id, professor_name)
        if p in self._professors:
            raise Professor.ProfessorAlreadyInSystemException()

        self._professors[p.id] = p

        return p

    def add_casa_de_burrito(self, cdb_id: int, cdb_name: str, dist: int, menu: set[str]) -> CasaDeBurrito:
        cdb = CasaDeBurrito(cdb_id, cdb_name, dist, menu)

        if cdb in self._casas_de_burrito:
            raise CasaDeBurrito.CasaDeBurritoAlreadyInSystemException()

        self._casas_de_burrito[cdb.id] = cdb

        return cdb

    @property
    def registered_professors(self):
        return list(self._professors.values())

    @property
    def registered_casas_de_burrito(self):
        return list(self._casas_de_burrito.values())

    def get_professor(self, professor_id: int) -> Professor:
        try:
            return self._professors[professor_id]
        except KeyError:
            raise Professor.ProfessorNotInSystemException()

    def get_casa_de_burrito(self, cdb_id: int) -> CasaDeBurrito:
        try:
            return self._casas_de_burrito[cdb_id]
        except KeyError:
            raise CasaDeBurrito.CasaDeBurritoNotInSystemException()

    def add_connection(self, p1: Professor, p2: Professor) -> CartelDeNachos:
        if p1 not in self._professors or p2 not in self._professors:
            raise Professor.ProfessorNotInSystemException()

        if p1 == p2:
            raise Professor.SameProfessorException()

        if p2 in p1.friends or p1 in p2.friends:
            raise Professor.ConnectionAlreadyExistsException()

        p1.add_friend(p2)
        p2.add_friend(p1)

        return self

    def favorites_by_rating(self, p: Professor) -> Collection[CasaDeBurrito]:
        return set([c for f in p.friends for c in f.favorites_by_rating(sys.maxsize)])

    def favorites_by_dist(self, p: Professor) -> Collection[CasaDeBurrito]:
        return set([c for f in p.friends for c in f.favorites_by_dist(sys.maxsize)])

    def get_recommendation(self, p: Professor, cdb: CasaDeBurrito, t: int) -> bool:
        reachable_from_p: List[int] = nx.single_source_shortest_path(self._connections_graph, p)[p.id]
        recommended_and_reachable_from_p = [p_id for p_id in reachable_from_p if
                                            cdb.is_rated_by(self._professors[p_id])]
        return any([p_id for p_id in recommended_and_reachable_from_p if reachable_from_p.index(p_id) >= t])

    def get_most_popular_restaurants_ids(self) -> list[int]:
        pass

    @property
    def _connections_graph(self) -> nx.Graph:
        g = nx.Graph()

        g.add_nodes_from(self._professors.keys())
        g.add_edges_from({{p1.id, p2.id} for p1 in self._professors.values() for p2 in p1.friends})

        return g

    def __str__(self) -> str:
        pass

    class ImpossibleConnectionException(BaseException):
        pass
