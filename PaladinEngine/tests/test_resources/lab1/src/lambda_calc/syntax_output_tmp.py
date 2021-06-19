import re
import sys
from functools import reduce
from typing import Optional, Tuple, Iterable

from PaladinEngine.stubs import __AS__, __FCS__, archive
from interactive_debugger import InteractiveDebugger
from source_provider import SourceProvider


class TreeWalk(object):
    class Visitor(object):

        def visit_node(self, tree_node):
            pass

        def done(self):
            return None

    def __init__(self, tree):
        self.tree = tree
        __AS__('self.tree', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=15)

    def __call__(self, visitor):
        __iter = self.__iter__()
        while True:
            try:
                x = __iter.__next__()
            except StopIteration:
                break
            visitor.visit_node(x)
        return visitor.done()

    def __iter__(self):
        raise NotImplementedError


class PreorderWalk(TreeWalk):

    def __iter__(self):
        stack = [self.tree]
        __AS__('stack', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=29)
        while stack:
            top = stack[0]
            __AS__('top', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=31)
            yield top
            stack[:1] = top.subtrees
            __AS__('stack', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=31)


class PostorderWalk(TreeWalk):

    def __iter__(self):
        (DOWN, UP) = (0, 1)
        __AS__('DOWN', 'UP', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=39)
        stack = [(DOWN, self.tree)]
        __AS__('stack', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=39)
        while stack:
            (direction, top) = stack.pop()
            __AS__('direction', 'top', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=42)
            if direction == UP:
                yield top
            else:
                stack += [(UP, top)] + [(DOWN, x) for x in top.subtrees]


class RichTreeWalk(object):
    """
    Provides advanced tree traversal by calling the visitor not only for each
    node, but also when entering and when leaving a subtree.
    @todo: The interface of RichTreeWalk does not match that of TreeWalk;
    should unify.
    """

    class Visitor(object):
        SKIP = ('skip',)
        __AS__('SKIP', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=58)

        def enter(self, subtree, prune=lambda: None):
            pass

        def leave(self, subtree):
            pass

        def join(self, node, prefix, infix, postfix):
            return None

        def done(self, root, final):
            return final

    def __init__(self, visitor):
        self.visitor = visitor
        __AS__('self.visitor', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=73)

    def __call__(self, tree):
        final = self._traverse(tree)
        __AS__('final', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=76)
        return self.visitor.done(tree, final)

    def _traverse(self, tree):
        descend = [1]
        __AS__('descend', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=80)
        prefix = self.visitor.enter(tree, descend.pop)
        __AS__('prefix', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=80)
        if prefix is self.Visitor.SKIP:
            return prefix
        elif descend:
            infix = self._descend(tree)
            __AS__('infix', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=85)
        else:
            infix = []
            __AS__('infix', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=87)
        postfix = self.visitor.leave(tree)
        __AS__('postfix', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=80)
        return self.visitor.join(tree, prefix, infix, postfix)

    def _descend(self, tree):
        return [self._traverse(sub) for sub in tree.subtrees]


class CollectVisitor(RichTreeWalk.Visitor):
    container = set
    __AS__('container', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=96)

    def __init__(self, container=None):
        if container is None:
            self.collection = self.container()
            __AS__('self.collection', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=100)
        else:
            self.collection = container
            __AS__('self.collection', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=102)

    def done(self):
        return self.collection


class Chart:

    def __init__(self, rows):
        """An Earley chart is a list of rows for every input word"""
        self.rows = rows
        __AS__('self.rows', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=111)

    def __len__(self):
        """Chart length"""
        return len(self.rows)

    def __repr__(self):
        """Nice string representation"""
        st = '<Chart>\n\t'
        __AS__('st', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=119)
        __iter = self.rows.__iter__()
        while True:
            try:
                r = __iter.__next__()
            except StopIteration:
                break
            st += r + '\n\t'
        st = st.removesuffix('\n\t')
        __AS__('st', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=119)
        st += '\n</Chart>'
        return st

    def add_row(self, row):
        """Add a row to chart, only if wasn't already there"""
        if not row in self.rows:
            self.rows.append(row)


class ChartRow:

    def __init__(self, rule, dot=0, start=0, previous=None, completing=None):
        """Initialize a chart row, consisting of a rule, a position
           index inside the rule, index of starting chart and
           pointers to parent rows"""
        self.rule = rule
        __AS__('self.rule', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=139)
        self.dot = dot
        __AS__('self.dot', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=139)
        self.start = start
        __AS__('self.start', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=139)
        self.completing = completing
        __AS__('self.completing', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=139)
        self.previous = previous
        __AS__('self.previous', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=139)

    def __len__(self):
        """A chart's length is its rule's length"""
        return len(self.rule)

    def __repr__(self):
        """Nice string representation:
            <Row <LHS -> RHS .> [start]>"""
        ____0 = list(self.rule.rhs)
        __FCS__(name='list', args=[self.rule.rhs], kwargs=[], return_value=____0, frame=sys._getframe(0),
                locals=locals(), globals=globals(), line_no=152)
        rhs = ____0
        __AS__('rhs', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=152)
        rhs.insert(self.dot, '.')
        rule_str = '[{0} -> {1}]'.format(self.rule.lhs, ' '.join(rhs))
        __AS__('rule_str', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=152)
        return '<Row {0} [{1}]> completes ({2}) follows ({3})'.format(rule_str, self.start, self.completing,
                                                                      self.previous)

    def __eq__(self, other):
        """Two rows are equal if they share the same rule, start and dot"""
        ____1 = len(self)
        __FCS__(name='len', args=[self], kwargs=[], return_value=____1, frame=sys._getframe(0), locals=locals(),
                globals=globals(), line_no=160)
        ____2 = len(other)
        __FCS__(name='len', args=[other], kwargs=[], return_value=____2, frame=sys._getframe(0), locals=locals(),
                globals=globals(), line_no=1)
        return ____1 == ____2 and self.dot == other.dot and (self.start == other.start) and (self.rule == other.rule)

    def is_complete(self):
        """Returns true if rule was completely parsed, i.e. the dot is at the end"""
        return len(self) - 1 == self.dot
        # return len(self) == self.dot

    def next_category(self):
        """Return next category to parse, i.e. the one after the dot"""
        ____3 = len(self)
        __FCS__(name='len', args=[self], kwargs=[], return_value=____3, frame=sys._getframe(0), locals=locals(),
                globals=globals(), line_no=176)
        x = ____3
        __AS__('x', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=176)
        if self.dot < x:
            return self.rule[self.dot]
        return None

    def prev_category(self):
        """Returns last parsed category"""
        if self.dot > 0:
            return self.rule[self.dot - 1]
        return None


class Word:

    def __init__(self, word='', tags=[]):
        """Initialize a word with a list of tags"""
        self.word = word
        __AS__('self.word', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=191)
        self.tags = tags
        __AS__('self.tags', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=191)

    def __repr__(self):
        """Nice string representation"""
        return '{0}<{1}>'.format(self.word, ','.join(self.tags))


class Sentence:

    def __init__(self, words=[]):
        """A sentence is a list of words"""
        self.words = words
        __AS__('self.words', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=202)

    def __str__(self):
        """Nice string representation"""
        s = ''
        __AS__('s', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=207)
        __iter = self.words.__iter__()
        while True:
            try:
                w = __iter.__next__()
            except StopIteration:
                break
            s += str(w) + ' '
        return s

    def __len__(self):
        """Sentence's length"""
        return len(self.words)

    def __getitem__(self, index):
        """Return a word of a given index"""
        ____4 = len(self)
        __FCS__(name='len', args=[self], kwargs=[], return_value=____4, frame=sys._getframe(0), locals=locals(),
                globals=globals(), line_no=219)
        lx = ____4
        __AS__('lx', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=219)
        if index >= 0 and index < lx:
            return self.words[index]
        else:
            return None

    def add_word(self, word):
        """Add word to sentence"""
        self.words.append(word)

    @staticmethod
    def from_string(text):
        """Create a Sentence object from a given string in the Apertium
           stream format:
              time/time<N> flies/flies<N>/flies<V> like/like<P>/like<V>
              an/an<D> arrow/arrow<N>"""
        lemmarex = re.compile('^[^\\/]*')
        __AS__('lemmarex', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=238)
        tagsrex = re.compile('\\/[^\\<]*\\<([^\\>]*)\\>')
        __AS__('tagsrex', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=238)
        ____5 = Sentence()
        __FCS__(name='Sentence', args=[], kwargs=[], return_value=____5, frame=sys._getframe(0), locals=locals(),
                globals=globals(), line_no=241)
        sentence = ____5
        __AS__('sentence', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=238)
        words = text.strip().split(' ')
        __AS__('words', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=238)
        __iter = words.__iter__()
        while True:
            try:
                word = __iter.__next__()
            except StopIteration:
                break
            lemma = lemmarex.match(word).group(0)
            __AS__('lemma', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=244)
            tags = tagsrex.findall(word)
            __AS__('tags', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=244)
            ____6 = Word(lemma, tags)
            __FCS__(name='Word', args=[lemma, tags], kwargs=[], return_value=____6, frame=sys._getframe(0),
                    locals=locals(), globals=globals(), line_no=246)
            w = ____6
            __AS__('w', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=244)
            sentence.add_word(w)
        return sentence


class Tree(object):

    def __init__(self, root, subtrees=None):
        self.root = root
        __AS__('self.root', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=255)
        if subtrees is None:
            self.subtrees = []
            __AS__('self.subtrees', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=257)
        else:
            self.subtrees = subtrees
            __AS__('self.subtrees', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=259)

    def __eq__(self, other):
        if not isinstance(other, Tree):
            return NotImplemented
        ____7 = type(self)
        __FCS__(name='type', args=[self], kwargs=[], return_value=____7, frame=sys._getframe(0), locals=locals(),
                globals=globals(), line_no=264)
        ____8 = type(other)
        __FCS__(name='type', args=[other], kwargs=[], return_value=____8, frame=sys._getframe(0), locals=locals(),
                globals=globals(), line_no=1)
        return ____7 == ____8 and (self.root, self.subtrees) == (other.root, other.subtrees)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        ____9 = tuple(self.subtrees)
        __FCS__(name='tuple', args=[self.subtrees], kwargs=[], return_value=____9, frame=sys._getframe(0),
                locals=locals(), globals=globals(), line_no=271)
        return hash((self.root, ____9))

    def repr(self, leaf_fmt):
        if self.subtrees:
            subreprs = ', '.join((x.repr(leaf_fmt) for x in self.subtrees))
            __AS__('subreprs', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=275)
            ____10 = leaf_fmt(self.root)
            __FCS__(name='leaf_fmt', args=[self.root], kwargs=[], return_value=____10, frame=sys._getframe(0),
                    locals=locals(), globals=globals(), line_no=276)
            return '%s{%s}' % (____10, subreprs)
        else:
            return leaf_fmt(self.root)

    def __repr__(self):
        return self.repr(repr)

    def __str__(self):
        return self.repr(str)

    def clone(self):
        return self.reconstruct(self)

    @classmethod
    def reconstruct(cls, t):
        return cls(t.root, [cls.reconstruct(s) for s in t.subtrees])

    @property
    def nodes(self):
        ____11 = PreorderWalk(self)
        __FCS__(name='PreorderWalk', args=[self], kwargs=[], return_value=____11, frame=sys._getframe(0),
                locals=locals(), globals=globals(), line_no=295)
        return list(____11)

    @property
    def leaves(self):
        return [n for n in PreorderWalk(self) if not n.subtrees]

    @property
    def terminals(self):
        """ @return a list of the values located at the leaf nodes. """
        return [n.root for n in self.leaves]

    @property
    def depth(self):
        """ Computes length of longest branch (iterative version). """
        stack = [(0, self)]
        __AS__('stack', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=309)
        max_depth = 0
        __AS__('max_depth', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=309)
        while stack:
            (depth, top) = stack[0]
            __AS__('depth', 'top', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=312)
            max_depth = max(depth, max_depth)
            __AS__('max_depth', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=312)
            stack[:1] = [(depth + 1, x) for x in top.subtrees]
            __AS__('stack', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=312)
        return max_depth

    def split(self, separator=None):
        if separator is None:
            separator = self.root
            __AS__('separator', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=318)
        if self.root == separator:
            return [item for s in self.subtrees for item in s.split(separator)]
        else:
            return [self]

    def fold(self):
        return type(self)(self.root, self.split())


class ParseTrees:

    def __init__(self, parser):
        """Initialize a syntax tree parsing process"""
        self.parser = parser
        __AS__('self.parser', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=336)
        self.charts = parser.charts
        __AS__('self.charts', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=336)
        self.length = len(parser)
        __AS__('self.length', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=336)
        self.nodes = []
        __AS__('self.nodes', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=336)
        __iter = parser.complete_parses.__iter__()
        while True:
            try:
                root = __iter.__next__()
            except StopIteration:
                break
            self.nodes.extend(self.build_nodes(root))

    def __len__(self):
        """Trees count"""
        return len(self.nodes)

    def __repr__(self):
        """String representation of a list of trees with indexes"""
        return '<Parse Trees>\n{0}</Parse Trees>'.format(
            '\n'.join(('Parse tree #{0}:\n{1}\n\n'.format(i + 1, str(self.nodes[i])) for i in range(len(self)))))

    def build_nodes(self, root):
        """Recursively create subtree for given parse chart row"""
        if root.completing:
            down = self.build_nodes(root.completing)
            __AS__('down', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=359)
        elif root.dot > 0:
            down = [Tree(root.prev_category())]
            __AS__('down', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=361)
        else:
            down = []
            __AS__('down', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=363)
        prev = root.previous
        __AS__('prev', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=366)
        left = []
        __AS__('left', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=366)
        if prev:
            left[:0] = [x.subtrees for x in self.build_nodes(prev)]
            __AS__('left', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=369)
            prev = prev.previous
            __AS__('prev', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=369)
        else:
            left = [[]]
            __AS__('left', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=372)
        __iter = left.__iter__()
        while True:
            try:
                x = __iter.__next__()
            except StopIteration:
                break
            x.extend(down)
        return [Tree(root.rule.lhs, subtrees) for subtrees in left]


class Parser:
    GAMMA_SYMBOL = 'γ'
    __AS__('GAMMA_SYMBOL', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=381)

    def __init__(self, grammar, sentence, debug=False):
        """Initialize parser with grammar and sentence"""
        self.grammar = grammar
        __AS__('self.grammar', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=385)
        self.sentence = sentence if isinstance(sentence, Sentence) else Sentence(sentence)
        __AS__('self.sentence', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=385)
        self.debug = debug
        __AS__('self.debug', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=385)
        self.charts = [Chart([]) for _ in range(len(self) + 1)]
        __AS__('self.charts', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=385)
        self.complete_parses = []
        __AS__('self.complete_parses', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=385)

    def __len__(self):
        """Length of input sentence"""
        return len(self.sentence)

    def init_first_chart(self):
        """Add initial Gamma rule to first chart"""
        row = ChartRow(Rule(Parser.GAMMA_SYMBOL, [self.grammar.start_symbol or 'S']), 0, 0)
        __AS__('row', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=399)
        self.charts[0].add_row(row)

    def prescan(self, chart, position):
        """Scan current word in sentence, and add appropriate
           grammar categories to current chart"""
        word = self.sentence[position - 1]
        __AS__('word', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=405)
        if word:
            rules = [Rule(tag, [word.word]) for tag in word.tags]
            __AS__('rules', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=407)
            __iter = rules.__iter__()
            while True:
                try:
                    rule = __iter.__next__()
                except StopIteration:
                    break
                chart.add_row(ChartRow(rule, 1, position - 1))

    def predict(self, chart, position):
        """Predict next parse by looking up grammar rules
           for pending categories in current chart"""
        __iter = chart.rows.__iter__()
        while True:
            try:
                row = __iter.__next__()
            except StopIteration:
                break
            next_cat = row.next_category()
            __AS__('next_cat', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=415)
            rules = self.grammar[next_cat]
            __AS__('rules', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=415)
            if rules:
                for rule in rules:
                    new = ChartRow(rule, 0, position)
                    __AS__('new', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=419)
                    chart.add_row(new)

    def complete(self, chart, position):
        """Complete a rule that was done parsing, and
           promote previously pending rules"""
        __iter = chart.rows.__iter__()
        while True:
            try:
                row = __iter.__next__()
            except StopIteration:
                break
            if row.is_complete():
                completed = row.rule.lhs
                __AS__('completed', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=427)
                for r in self.charts[row.start].rows:
                    if completed == r.next_category():
                        new = ChartRow(r.rule, r.dot + 1, r.start, r, row)
                        __AS__('new', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=430)
                        chart.add_row(new)

    def parse(self):
        """Main Earley's Parser loop"""
        self.init_first_chart()
        i = 0
        __AS__('i', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=437)
        while i < len(self.charts):
            chart = self.charts[i]
            __AS__('chart', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=440)
            self.prescan(chart, i)
            length = len(chart)
            __AS__('length', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=440)
            old_length = -1
            __AS__('old_length', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=440)
            while old_length != length:
                self.predict(chart, i)
                self.complete(chart, i)
                old_length = length
                __AS__('old_length', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=451)
                length = len(chart)
                __AS__('length', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=451)
            i += 1
        if self.debug:
            print('Parsing charts:')
            __iter = range(len(self.charts)).__iter__()
            while True:
                try:
                    i = __iter.__next__()
                except StopIteration:
                    break
                print('-----------{0}-------------'.format(i))
                print(self.charts[i])
                print('-------------------------'.format(i))

    def is_valid_sentence(self):
        """Returns true if sentence has a complete parse tree"""
        res = False
        __AS__('res', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=466)
        __iter = self.charts[-1].rows.__iter__()
        while True:
            try:
                row = __iter.__next__()
            except StopIteration:
                break
            if row.start == 0:
                if row.rule.lhs == self.GAMMA_SYMBOL:
                    if row.is_complete():
                        self.complete_parses.append(row)
                        res = True
                        __AS__('res', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=472)
        return res


class Rule:

    def __init__(self, lhs, rhs):
        """Initializes grammar rule: LHS -> [RHS]"""
        self.lhs = lhs
        __AS__('self.lhs', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=479)
        self.rhs = rhs
        __AS__('self.rhs', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=479)

    def __len__(self):
        """A rule's length is its RHS's length"""
        return len(self.rhs)

    def __repr__(self):
        """Nice string representation"""
        return '<Rule {0} -> {1}>'.format(self.lhs, ' '.join(self.rhs))

    def __getitem__(self, item):
        """Return a member of the RHS"""
        return self.rhs[item]

    def __eq__(self, other):
        """Rules are equal iff both their sides are equal"""
        if self.lhs == other.lhs:
            if self.rhs == other.rhs:
                return True
        return False


class Grammar:

    def __init__(self):
        """A grammar is a collection of rules, sorted by LHS"""
        self.rules = {}
        __AS__('self.rules', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=505)
        self.start_symbol = None
        __AS__('self.start_symbol', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=505)

    def __repr__(self):
        """Nice string representation"""
        st = '<Grammar>\n'
        __AS__('st', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=510)
        __iter = self.rules.values().__iter__()
        while True:
            try:
                group = __iter.__next__()
            except StopIteration:
                break
            for rule in group:
                st += '\t{0}\n'.format(str(rule))
        st += '</Grammar>'
        return st

    def __getitem__(self, lhs):
        """Return rules for a given LHS"""
        if lhs in self.rules:
            return self.rules[lhs]
        else:
            return None

    def add_rule(self, rule):
        """Add a rule to the grammar"""
        lhs = rule.lhs
        __AS__('lhs', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=526)
        if lhs in self.rules:
            self.rules[lhs].append(rule)
        else:
            d = self.rules
            __AS__('d', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=531)
            d[lhs] = [rule]
            # __AS__(('d', 'lhs'), locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=531)
        if self.start_symbol is None:
            self.start_symbol = lhs
            __AS__('self.start_symbol', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=535)

    @staticmethod
    def from_file(filename):
        """Returns a Grammar instance created from a text file.
        """
        return Grammar.from_lines(open(filename))

    @staticmethod
    def from_string(string):
        """Returns a Grammar instance created from a string.
        """
        return Grammar.from_lines(string.splitlines())

    @staticmethod
    def from_lines(iterable):
        """Returns a Grammar instance created from an iterator over lines.
           The lines should have the format:
               lhs -> outcome | outcome | outcome"""
        grammar = Grammar()
        __AS__('grammar', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=555)
        __iter = iterable.__iter__()
        while True:
            try:
                line = __iter.__next__()
            except StopIteration:
                break
            comm = line.find('#')
            __AS__('comm', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=558)
            if comm >= 0:
                line = line[:comm]
                __AS__('line', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=560)
            line = line.strip()
            __AS__('line', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=558)
            if line == '':
                continue
            rule = line.split('->', 1)
            __AS__('rule', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=558)
            if len(rule) != 2:
                raise ValueError("invalid grammar format: '%s'" % line)
            lhs = rule[0].strip()
            __AS__('lhs', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=558)
            for outcome in rule[1].split('|'):
                rhs = outcome.strip()
                __AS__('rhs', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=571)
                symbols = rhs.split(' ') if rhs else []
                __AS__('symbols', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=571)
                r = Rule(lhs, symbols)
                __AS__('r', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=571)
                grammar.add_rule(r)
        return grammar


class SillyLexer(object):
    TEXT = 1
    __AS__('TEXT', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=580)
    TOKEN = 2
    __AS__('TOKEN', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=580)

    def __init__(self, token_regexp):
        if not isinstance(token_regexp, str):
            if isinstance(token_regexp, Iterable):
                token_regexp = '|'.join(token_regexp)
                __AS__('token_regexp', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=586)
            else:
                raise ValueError('invalid token specification')
        self.token_re = re.compile(token_regexp)
        __AS__('self.token_re', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=589)

    def __call__(self, input_text):
        __iter = self.raw(input_text).__iter__()
        while True:
            try:
                (a, val) = __iter.__next__()
            except StopIteration:
                break
            if a == self.TOKEN:
                yield val

    def raw(self, input_text):
        pos = 0
        __AS__('pos', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=597)
        __iter = self.token_re.finditer(input_text).__iter__()
        while True:
            try:
                mo = __iter.__next__()
            except StopIteration:
                break
            (from_, to) = mo.span()
            __AS__('from_', 'to', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=600)
            if from_ > pos:
                yield (self.TEXT, input_text[from_:pos])
            yield (self.TOKEN, self.mktoken(mo))
            pos = to
            __AS__('pos', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=600)

    def mktoken(self, mo):
        return Word(mo.group(), [mo.lastgroup or mo.group()])


class SillyBlocker(object):

    def __init__(self, open_token, close_token):
        self.topen = open_token
        __AS__('self.topen', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=613)
        self.tclose = close_token
        __AS__('self.tclose', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=613)

    def __call__(self, token_stream):
        bal = 0
        __AS__('bal', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=617)
        (topen, tclose) = (self.topen, self.tclose)
        __AS__('topen', 'tclose', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=617)
        bag = []
        __AS__('bag', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=617)
        __iter = token_stream.__iter__()
        while True:
            try:
                t = __iter.__next__()
            except StopIteration:
                break
            if t == topen:
                bal += 1
            elif t == tclose:
                bal -= 1
            bag += [t]
            if bal == 0:
                yield Tree(t, list(self(bag[1:-1])))
                bag = []
                __AS__('bag', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=628)
        if bal != 0:
            raise SyntaxError("unbalanced '%s' and '%s'" % (self.topen, self.tclose))


class LambdaParser(object):
    TOKENS = '(let|in)(?![\\w\\d_])   (?P<id>[^\\W\\d]\\w*)   (?P<num>\\d+)   [\\\\.()=]'.split()
    __AS__('TOKENS', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=635)
    GRAMMAR = "    E    ->  \\. | let_    |   E1  |  E1'\n    E1   ->  @            |   E0\n    E1'  ->  @'           |   E0\n    E0   ->  id | num     |  ( E )\n    \\.   ->  \\ L . E \n    @    ->  E1 E0\n    @'   ->  E1 \\.\n    L    ->  id L |\n    let_ ->  let id = E in E\n    "
    __AS__('GRAMMAR', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=635)

    def __init__(self):
        self.tokenizer = SillyLexer(self.TOKENS)
        __AS__('self.tokenizer', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=649)
        self.grammar = Grammar.from_string(self.GRAMMAR)
        __AS__('self.grammar', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=649)

    def __call__(self, program_text: str) -> Optional[Tree]:
        tokens = list(self.tokenizer(program_text))
        __AS__('tokens', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=653)
        earley = Parser(grammar=self.grammar, sentence=tokens, debug=False)
        __AS__('earley', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=653)
        earley.parse()
        if earley.is_valid_sentence():
            trees = ParseTrees(earley)
            __AS__('trees', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=659)
            assert len(trees) == 1
            return self.postprocess(trees.nodes[0])
        else:
            return None

    def postprocess(self, t: Tree) -> Tree:
        if t.root in ['γ', 'E', 'E0', 'E1', "E1'"] and len(t.subtrees) == 1:
            return self.postprocess(t.subtrees[0])
        elif t.root == 'E0' and t.subtrees[0].root == '(':
            return self.postprocess(t.subtrees[1])
        elif t.root == '\\.':
            args = t.subtrees[1].split()
            __AS__('args', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=671)
            t = reduce(lambda t, a: Tree('\\', [a, t]), reversed(args), t.subtrees[3])
            __AS__('t', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=671)
        elif t.root == "@'":
            t = Tree('@', t.subtrees)
            __AS__('t', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=674)
        elif t.root == 'L':
            t = Tree('.', t.split())
            __AS__('t', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=676)
        return Tree(t.root, [self.postprocess(s) for s in t.subtrees])


'''
Formats an expression for pretty printing.
Should be called as pretty(e), admitting the default values for `parent` and `follow`; 
these values are suitable for the top-level term.
They are used subsequently by recursive calls.
'''


def pretty(expr: Tree, parent: Tuple[str, int] = ('.', 0), follow: str = '') -> str:
    if expr.root in ['id', 'num']:
        return expr.subtrees[0].root
    if expr.root == '\\':
        tmpl = '\\%s. %s'
        __AS__('tmpl', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=693)
        if parent == ('@', 0) or parent[0] == follow == '@':
            tmpl = '(%s)' % tmpl
            __AS__('tmpl', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=695)
    elif expr.root == '@':
        tmpl = '%s %s'
        __AS__('tmpl', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=697)
        if parent == ('@', 1):
            tmpl = '(%s)' % tmpl
            __AS__('tmpl', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=699)
    else:
        return str(expr)
    n = len(expr.subtrees)
    __AS__('n', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=703)
    return tmpl % tuple(
        (pretty(s, (expr.root, i), expr.root if i < n - 1 else follow) for (i, s) in enumerate(expr.subtrees)))


if __name__ == '__main__':
    parser = LambdaParser()
    __AS__('parser', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=710)
    expr = parser('\\x. x \\z g. y 6')
    __AS__('expr', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=710)
    parser = LambdaParser()
    __AS__('parser', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=710)
    expr2 = parser('\\x. x \\z g. y 6 5 4')
    __AS__('expr2', locals=locals(), globals=globals(), frame=sys._getframe(0), line_no=710)
    if expr:
        print('>> Valid expression.')
        print(expr)
    else:
        print('>> Invalid expression.')
        # Initialize PaLaDinInteractiveDebugger.
        with open(
                '/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/test_resources/lab1/src/lambda_calc'
                '/syntax.py', 'r') as f:
            SourceProvider.set_code(''.join(f.readlines()))

        interactive_debugger = InteractiveDebugger(archive, "print('>> Invalid expression.')", 720)
        interactive_debugger.cmdloop()
