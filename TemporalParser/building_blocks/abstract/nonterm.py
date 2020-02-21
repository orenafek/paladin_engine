from lrparsing import Nonterm as _Nonterm

from TemporalParser.building_blocks.abstract.collectible import Collectible


class Nonterm(_Nonterm, Collectible):
    def __init__(self, *args):
        super().__init__(*args)
        super(_Nonterm, self).__init__()

    def collect(self, value):
        print(f"Nonterm::collect: value = {value}")
