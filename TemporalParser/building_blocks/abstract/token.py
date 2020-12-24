from lrparsing import Token as _Token

from TemporalParser.building_blocks.abstract.collectible import Collectible


class Token(_Token, Collectible):
    def __init__(self, literal=None, re=None, case=None, kind=None, refine=None):
        super().__init__(literal, re, case, kind, refine)
        super(_Token).__init__()
        self.__value = ""

    def collect(self, value):
        print(f"Token::collect: value = {value}")

    def __or__(self, other):
        return super().__or__(other)
