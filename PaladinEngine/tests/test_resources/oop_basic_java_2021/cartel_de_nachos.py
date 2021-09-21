from typing import Collection

from tests.test_resources.oop_basic_java_2021.casa_de_burrito import CasaDeBurrito
from tests.test_resources.oop_basic_java_2021.professor import Professor


class CartelDeNachos(object):
    ...


class CartelDeNachos(object):

    def join_cartel(self, professor_id: int, professor_name: str) -> Professor:
        pass

    def add_casa_de_burrito(self, cdb_id: int, cdb_name: str, dist: int, menu: set[str]) -> CasaDeBurrito:
        pass

    @property
    def registered_professors(self):
        pass

    @property
    def registered_casas_de_burrito(self):
        pass

    def get_professor(self, professor_id: int) -> Professor:
        pass

    def get_casa_de_burrito(self, cdb_id: int) -> CasaDeBurrito:
        pass

    def add_connection(self, p1: Professor, p2: Professor) -> CartelDeNachos:
        pass

    def favorites_by_rating(self, p: Professor) -> Collection[CasaDeBurrito]:
        pass

    def favorites_by_dist(self, p: Professor) -> Collection[CasaDeBurrito]:
        pass

    def get_recommendation(self, p: Professor, cdb: CasaDeBurrito, t: int) -> bool:
        pass

    def get_most_popular_restaurants_ids(self) -> list[int]:
        pass

    def __str__(self) -> str:
        pass

    class ImpossibleConnectionException(Exception):
        pass
