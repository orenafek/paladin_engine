from abc import ABC, abstractmethod

from lrparsing import Rule

from TemporalParser.building_blocks.abstract.token import Token
from TemporalParser.building_blocks.building_blocks import building_blocks


class Collector(ABC):

    @abstractmethod
    def collect(self, stack: list, target, *components) -> (list, object):
        raise NotImplementedError()


class RuleCollector(Collector):
    def collect(self, stack: list, rule: Rule, *components) -> (list, object):
        # Convert rule name.
        rule_name = ''.join(word.title() for word in rule.identifier.split('_'))
        # Extract rule's class
        nonterm_class = building_blocks[rule_name]

        # Create nonterm object.
        nonterm = nonterm_class(*components)

        for component in components:
            if type(component[1]) is tuple:
                continue
            stack.append(component[1])

        # Collect rule.
        stack = nonterm.collect(stack)

        # Push parsed to stack.
        stack.append(nonterm)

        return stack


class TokenCollector(Collector):

    def collect(self, stack: list, token: Token, *components) -> (list, object):
        return stack
