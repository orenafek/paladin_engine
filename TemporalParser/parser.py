import lrparsing
from lrparsing import List, Prio, Ref

from TemporalParser.building_blocks.abstract.keyword import Keyword
from TemporalParser.building_blocks.abstract.token import Token
from TemporalParser.condition.condition import always, eventually, never
from TemporalParser.rule_collector.rule_collector import RuleCollector, TokenCollector


class Parser(object):

    def __init__(self):
        pass

    class ParserGrammar(lrparsing.Grammar):
        class T(lrparsing.TokenRegistry):
            ident = Token(re="[A-Za-z_][A-Za-z_0-9]*")
            first = Keyword(literal="first")
            last = Keyword(literal="last")
            since = Keyword(literal="since")
            immediate = Keyword(literal="immediate")
            change_data = Keyword(literal="change_data")
            never = Keyword(literal="never")
            always = Keyword(literal="always")
            eventually = Keyword(literal="eventually")

        time_connector = T.first | T.last | T.since

        condition = always | eventually | never
        func_call = T.ident + '(' + List(T.ident, ',') + ')'
        method_call = T.ident + '.' + func_call
        # call = call | method_call
        call = Prio(
            method_call,
            func_call
        )
        event = T.immediate | call | T.change_data
        phrase = Ref("phrase")
        # phrase = time_connector + event + condition + phrase | event
        simple_phrase = event * 1
        complex_phrase = time_connector + event + condition + phrase
        phrase = simple_phrase | complex_phrase
        START = phrase

    def parse(self, s, tree_factory=None, log=None):
        return Parser.ParserGrammar.parse(s, tree_factory=tree_factory)


if __name__ == '__main__':
    # parse_tree = Parser().ExprParser.parse("1 + /* a */ b + 3 * 4 is c(1, a)")
    # print(Parser().ExprParser.repr_parse_tree(parse_tree))
    l = []

    rule_collector = RuleCollector()
    token_collector = TokenCollector()
    stack = []


    def tree_factory(x):

        global stack
        # Extract target
        target = x[0]

        if type(target) is lrparsing.Token:
            # The target is not a part of our parsing tree.
            return x

        if target is Parser.ParserGrammar.START:
            return x

        # Choose collector.
        if isinstance(target, Token):
            collector = token_collector
        else:
            collector = rule_collector

        # Collect rule.

        updated_stack = collector.collect(stack, target, *x[1::])
        stack = updated_stack

        return x


    def log(*x):
        print(x)


    tree = Parser().parse("since b.draw(win) never b.undraw(win)", tree_factory)

    x = Parser.ParserGrammar.repr_parse_tree(tree)
    # print(x)
    print(tree)
