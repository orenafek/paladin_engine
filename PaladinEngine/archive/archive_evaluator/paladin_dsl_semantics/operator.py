from abc import ABC
from dataclasses import dataclass
from typing import Optional, Iterable, Dict, Collection, List, Type, Callable, Any

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.object_builder.object_builder import ObjectBuilder


@dataclass
class Operator(ABC):

    def __init__(self, times: Optional[Iterable[Time]] = None):
        self._times = times

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        raise NotImplementedError()

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @property
    def times(self):
        if isinstance(self._times, range):
            return self._times

        # Assuming here that _times is an iterable of ranges.
        result = []
        for t in self._times:
            if isinstance(t, range):
                result.extend(list(t))

            elif isinstance(t, Time):
                result.append(t)

            else:
                raise TypeError(f'A weird time of type {type(t)}')

        return result

    @times.setter
    def times(self, value):
        self._times = value

    def _get_args(self) -> Collection['Operator']:
        raise NotImplementedError()

    def update_times(self, times) -> 'Operator':
        self.times = times

        for a in self._get_args():
            a.times = times
            a.update_times(times)

        return self

    @classmethod
    def all(cls) -> List[Type['Operator']]:
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            subclasses.extend(subclass.all())

        return list(set(subclasses))

    @classmethod
    def _all(cls):
        return cls.__subclasses__()

    @classmethod
    def is_operator(cls, name: Any) -> bool:
        return any(map(lambda o: o.name() == name, cls.all()))


class NoArgOperator(Operator, ABC):
    def _get_args(self) -> Collection['Operator']:
        return []


class UniLateralOperator(Operator, ABC):
    def __init__(self, times: Iterable[Time], first: Operator):
        super(UniLateralOperator, self).__init__(times)
        self.first = first

    def _get_args(self) -> Collection['Operator']:
        return [self.first]


class OptionalArgOperator(UniLateralOperator, ABC):
    def __init__(self, times: Iterable[Time], first: Optional[Operator] = None):
        super().__init__(times, first)

    def _get_args(self) -> Collection['Operator']:
        return [self.first] if self.first else []


class BiLateralOperator(Operator, ABC):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        super(BiLateralOperator, self).__init__(times)
        self.first: Operator = first
        self.second: Operator = second

    def _get_args(self) -> Collection['Operator']:
        return [self.first, self.second]


class TriLateralOperator(Operator, ABC):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator, third: Operator):
        super(TriLateralOperator, self).__init__(times)
        self.first: Operator = first
        self.second: Operator = second
        self.third: Operator = third

    def _get_args(self) -> Collection['Operator']:
        return [self.first, self.second, self.third]


class VariadicLateralOperator(Operator, ABC):
    def __init__(self, times: Iterable[Time], *args: Operator, **kwargs: Operator):
        super(VariadicLateralOperator, self).__init__(times)
        self.args: List[Operator] = list(args)
        self.kwargs: Dict[str, Operator] = kwargs

    def _get_args(self) -> Collection['Operator']:
        return self.args
