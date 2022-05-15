from abc import ABC, abstractmethod
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *

SemanticsArgType = Union[bool, EvalResult]


def first_satisfaction(formula: EvalResult) -> Union[int, bool]:
    for time in formula:
        result, replacements = formula[time]
        if result:
            return time

    return False


def last_satisfaction(formula: EvalResult) -> Union[int, bool]:
    return first_satisfaction({t: r for (t, r) in reversed(formula.items())})


class Operator(ABC):
    @abstractmethod
    def eval(self, *args):
        raise NotImplementedError()

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    def create_eval(self, *args):
        return lambda parser: self.eval(*[f(parser) for f in (args[2].asList())[0][1:]])


class UniLateralOperator(Operator):
    @abstractmethod
    def eval(self, arg):
        raise NotImplementedError()


class BiLateralOperator(Operator):
    @abstractmethod
    def eval(self, arg1, arg2):
        raise NotImplementedError()


class Globally(UniLateralOperator):
    @property
    def name(self):
        return "G"

    def eval(self, formula: SemanticsArgType):
        return Release().eval(False, formula)


class Release(BiLateralOperator):
    @property
    def name(self):
        return "R"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        return Not().eval(Until().eval(Not().eval(arg1), Not().eval(arg2)))


class Finally(UniLateralOperator):
    @property
    def name(self):
        return "F"

    def eval(self, arg: SemanticsArgType):
        return Until().eval(True, arg)


class Next(UniLateralOperator):
    @property
    def name(self):
        return "X"

    def eval(self, arg: SemanticsArgType):
        if arg is bool:
            """
            X(T) = T
            X(F) = F
            """
            return arg

        # TODO: Should I check for satisfaction? I.e., return {t:r for ... in ... ** if r[0] **} ??
        return {t: r for (t, r) in arg.items()[1::]}


class Until(BiLateralOperator):
    @property
    def name(self):
        return "U"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        if type(arg1) is bool and type(arg2) is bool:
            """
            U(T, T) = T
            U(T, F) = U(F, T) = F
            U(F, F) = F
            """
            return arg1 and arg2

        if type(arg1) is bool and type(arg2) is dict:
            if arg1:
                """
                U(T, ϕ) = ϕ 
                """
                return arg2

            """
            U(F, ϕ) = F
            """
            return False

        if type(arg1) is dict and type(arg2) is bool:
            if arg2:
                """
                ω ⊨ U(ϕ, T) ↔ ∃i >= 0, ω_i ⊨ ϕ  
                """
                return {t: r for (t, r) in arg1.items() if t >= first_satisfaction(arg1)}

            return False

        # Both formulas are of type EvalResult:
        """
        ω ⊨ U(ϕ, ψ) ↔ ∃i >= 0, ω_i ⊨ ψ ∧ ∀ <= 0 k <= i, ω_k ⊨ ϕ  
        """
        formula2_first_satisfaction = first_satisfaction(arg2)
        if not formula2_first_satisfaction:
            return False

        return {t: r1 for (t, r1) in arg1.items() if t <= formula2_first_satisfaction and r1[0]}


class Or(BiLateralOperator):
    @property
    def name(self):
        return "∨"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        if type(arg1) is bool and type(arg2) is bool:
            return arg1 or arg2

        if type(arg1) is bool and type(arg2) is dict:
            if arg1:
                return True

            return arg2

        if type(arg1) is dict and type(arg2) is bool:
            if arg2:
                return True

            return arg1

        return {t: (r1[0] or r2[0], r1[1] + r2[1]) for t, r1 in arg1.items() for t2, r2 in arg2.items()}


class Not(UniLateralOperator):
    @property
    def name(self):
        return "N"

    def eval(self, arg: SemanticsArgType):
        if type(arg) is bool:
            return not arg

        return {t: (not r[0], r[1]) for (t, r) in arg.items()}


class And(BiLateralOperator):
    @property
    def name(self):
        return "∧"

    def eval(self, arg1: SemanticsArgType, arg2: SemanticsArgType):
        return Not().eval(Or().eval(Not().eval(arg1), Not().eval(arg2)))


class Before(BiLateralOperator):
    @property
    def name(self) -> str:
        return "B"

    def eval(self, arg1, arg2):
        return Until().eval(Not().eval(Globally().eval(Not().eval(arg1))), arg2)


class After(BiLateralOperator):
    @property
    def name(self) -> str:
        return "A"

    def eval(self, arg1, arg2):
        return Before().eval(arg2, arg1)


class AllFuture(UniLateralOperator):
    @property
    def name(self) -> str:
        return "₣"

    def eval(self, arg):
        return Globally().eval(Next().eval(arg))


UniLateralOperator.ALL = UniLateralOperator.__subclasses__()
BiLateralOperator.ALL = BiLateralOperator.__subclasses__()
Operator.ALL = UniLateralOperator.ALL + BiLateralOperator.ALL
