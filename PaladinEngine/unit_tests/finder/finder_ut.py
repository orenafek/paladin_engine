import ast
import unittest

from finders import SubscriptFinder


class TestSubscriptFinder(unittest.TestCase):

    def setUp(self) -> None:
        self.finder = SubscriptFinder()


    def basic_test(self, code_str):
        # Parse the code string to an ast.
        module = ast.parse(code_str)

        # Visit.
        self.finder.visit(module)

        # Find.
        return self.finder.find()

    def test_dictionary_subscript(self):
        for se in self.basic_test('d[1] = 2'):
            print(str(se))



if __name__ == "__main__":
    unittest.main()