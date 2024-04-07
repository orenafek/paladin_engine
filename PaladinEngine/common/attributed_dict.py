from typing import Dict


class AttributedDict(Dict):

    def __init__(self, seq=None) -> None:
        if seq:
            super().__init__(seq)

        for k, v in self.items():
            self.__setattr__(str(k), v)

    def __hash__(self) -> int:
        return hash(str(self))

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__setattr__(str(key), value)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.__delattr__(key)
