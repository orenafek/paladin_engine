import astor

from engine import PaLaDiNEngine
from finders import ParametrizedFunctionCallFinder


def main():
    finder = ParametrizedFunctionCallFinder()
    # Read source file.
    with open(r'tests\test_resources\test_module.py') as f:
        # Read the source file.
        tetris_source_file = f.read()

        # Transform into a PaLaDiN form.
        module = PaLaDiNEngine.create_module(tetris_source_file)

        finder.visit(module)

        print([astor.to_source(c) for c in finder.find()])


if __name__ == '__main__':
    main()
