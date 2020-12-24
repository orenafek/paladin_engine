from TemporalParser.building_blocks.abstract.token import Token


class Keyword(Token):
    def __init__(self, literal, case=None):
        super().__init__(literal, case=case, kind=Token.KEYWORD)

    def collect(self, value):
        print(f"Keyword::collect: value = {value}")
