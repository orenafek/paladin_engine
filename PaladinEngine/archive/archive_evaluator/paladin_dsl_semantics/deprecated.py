from typing import Type


def Deprecated(cls: Type):
    cls.deprecated = True
    return cls
