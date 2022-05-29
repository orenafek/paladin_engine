import sys
import pathlib

# hack :)
sys.path[:0] = [str(pathlib.Path(__file__).parent.parent.parent / 'lib')]
