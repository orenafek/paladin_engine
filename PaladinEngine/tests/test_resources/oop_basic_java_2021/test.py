import unittest

from tests.test_resources.oop_basic_java_2021.code import *


class MyTestCase(unittest.TestCase):
    def test_example(self):
        network = CartelDeNachos()
        try:
            p1 = network.join_cartel(100, "Anne")
            p2 = network.join_cartel(300, "Ben")
        except Professor.ProfessorAlreadyInSystemException:
            self.fail()

        menu1 = {'Hamburger', 'Fries'}
        menu2 = {'Steak', 'Fries','Orange Juice'}

        try:
            r1 = network.add_casa_de_burrito(10, 'BBB', 12, menu1)
            r2 = network.add_casa_de_burrito(12, "Bob's place", 5, menu2)
            r3 = network.add_casa_de_burrito(14, "Ben's hut", 1, menu2)
        except CasaDeBurrito.CasaDeBurritoAlreadyInSystemException:
            self.fail()

        try:
            r1.rate(p1, 4).rate(p2, 5)
            r2.rate(p1, 2).rate(p1, 3).rate(p2, 4)
            r3.rate(p2, 4)
        except CasaDeBurrito.RateRangeException:
            self.fail()

        self.assertEqual(2, r1.number_of_rates())
        self.assertEqual(3.5, r2.average_rating())

        try:
            p1.favorite(r1).favorite(r2)
            p2.favorite(r2).favorite(r3)
        except Professor.UnratedFavoriteCasaDeBurritoException:
            self.fail()




if __name__ == '__main__':
    unittest.main()
