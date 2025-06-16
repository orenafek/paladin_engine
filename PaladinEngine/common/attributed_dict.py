from typing import Dict, Any, Union


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

    def __sub__(self, other: Union['AttributedDict', Any]):
        if not isinstance(other, AttributedDict):
            raise TypeError(f'unsupported operand type(s) for -: \'{dict.__name__}\' and \'{type(other).__name__}\'')

        sk = set(self.keys())
        ok = set(other.keys())
        joint_keys = sk.intersection(ok)

        keys_only_in_self = sk.difference(ok)

        #return AttributedDict({**{k:self[k] for k in keys_only_in_self}, **{k:}})