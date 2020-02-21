from lrparsing import BinOp as _BinOp, OpOr as _OpOr

from TemporalParser.building_blocks.abstract.collectible import Collectible


class BinOp(_BinOp, Collectible):
    def collect(self, value):
        print(f"BinOp::collect, value = {value}")


class OpOr(_OpOr, Collectible):
    def collect(self, value):
        print(f"BinOp::collect, value = {value}")
