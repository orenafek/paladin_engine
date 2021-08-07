import csv

from stubs.stubs import __FLI__, __POST_CONDITION__, __FC__, __AS__, __FRAME__, archive

from typing import Tuple, Optional, Iterable
from functools import reduce
from collections import namedtuple
import re
import matplotlib
import matplotlib.pyplot as plt

archive.pause_record()
class TreeWalk(object):

    class Visitor(object):

        def visit_node(self, tree_node):
            pass

        def done(self):
            return None

    def __init__(self, tree):
        self.tree = tree
        __AS__('self.tree = tree', 'self.tree', locals=locals(), globals=globals(), frame=__FRAME__, line_no=15)

    def __call__(self, visitor):
        __iter = self.__iter__()
        while True:
            try:
                x = __iter.__next__()
            except StopIteration:
                break
            __FC__('visitor.visit_node(x)', visitor.visit_node, locals(), globals(), __FRAME__, 19, x)
        return __FC__('visitor.done()', visitor.done, locals(), globals(), __FRAME__, 20)

    def __iter__(self):
        raise NotImplementedError

class PreorderWalk(TreeWalk):

    def __iter__(self):
        stack = [self.tree]
        __AS__('stack = [self.tree]', 'stack', locals=locals(), globals=globals(), frame=__FRAME__, line_no=29)
        while stack:
            top = stack[0]
            __AS__('top = stack[0]', 'top', locals=locals(), globals=globals(), frame=__FRAME__, line_no=31)
            yield top
            stack[:1] = top.subtrees
            __AS__('stack[:1] = top.subtrees', 'stack[:1:]', locals=locals(), globals=globals(), frame=__FRAME__, line_no=31)

class PostorderWalk(TreeWalk):

    def __iter__(self):
        (DOWN, UP) = (0, 1)
        __AS__('(DOWN, UP) = (0, 1)', 'UP', locals=locals(), globals=globals(), frame=__FRAME__, line_no=39)
        __AS__('(DOWN, UP) = (0, 1)', 'DOWN', locals=locals(), globals=globals(), frame=__FRAME__, line_no=39)
        stack = [(DOWN, self.tree)]
        __AS__('stack = [(DOWN, self.tree)]', 'stack', locals=locals(), globals=globals(), frame=__FRAME__, line_no=39)
        while stack:
            (direction, top) = __FC__('stack.pop()', stack.pop, locals(), globals(), __FRAME__, 42)
            __AS__('(direction, top) = stack.pop()', 'top', locals=locals(), globals=globals(), frame=__FRAME__, line_no=42)
            __AS__('(direction, top) = stack.pop()', 'direction', locals=locals(), globals=globals(), frame=__FRAME__, line_no=42)
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
        __AS__("SKIP = ('skip',)", 'SKIP', locals=locals(), globals=globals(), frame=__FRAME__, line_no=58)

        def enter(self, subtree, prune=lambda : None):
            pass

        def leave(self, subtree):
            pass

        def join(self, node, prefix, infix, postfix):
            return None

        def done(self, root, final):
            return final

    def __init__(self, visitor):
        self.visitor = visitor
        __AS__('self.visitor = visitor', 'self.visitor', locals=locals(), globals=globals(), frame=__FRAME__, line_no=73)

    def __call__(self, tree):
        final = __FC__('self._traverse(tree)', self._traverse, locals(), globals(), __FRAME__, 76, tree)
        __AS__('final = self._traverse(tree)', 'final', locals=locals(), globals=globals(), frame=__FRAME__, line_no=76)
        return __FC__('self.visitor.done(tree, final)', self.visitor.done, locals(), globals(), __FRAME__, 77, tree, final)

    def _traverse(self, tree):
        descend = [1]
        __AS__('descend = [1]', 'descend', locals=locals(), globals=globals(), frame=__FRAME__, line_no=80)
        prefix = __FC__('self.visitor.enter(tree, descend.pop)', self.visitor.enter, locals(), globals(), __FRAME__, 81, tree, descend.pop)
        __AS__('prefix = self.visitor.enter(tree, descend.pop)', 'prefix', locals=locals(), globals=globals(), frame=__FRAME__, line_no=80)
        if prefix is self.Visitor.SKIP:
            return prefix
        elif descend:
            infix = __FC__('self._descend(tree)', self._descend, locals(), globals(), __FRAME__, 85, tree)
            __AS__('infix = self._descend(tree)', 'infix', locals=locals(), globals=globals(), frame=__FRAME__, line_no=85)
        else:
            infix = []
            __AS__('infix = []', 'infix', locals=locals(), globals=globals(), frame=__FRAME__, line_no=87)
        postfix = __FC__('self.visitor.leave(tree)', self.visitor.leave, locals(), globals(), __FRAME__, 88, tree)
        __AS__('postfix = self.visitor.leave(tree)', 'postfix', locals=locals(), globals=globals(), frame=__FRAME__, line_no=80)
        return __FC__('self.visitor.join(tree, prefix, infix, postfix)', self.visitor.join, locals(), globals(), __FRAME__, 89, tree, prefix, infix, postfix)

    def _descend(self, tree):
        return [__FC__('self._traverse(sub)', self._traverse, locals(), globals(), __FRAME__, 92, sub) for sub in tree.subtrees]

class CollectVisitor(RichTreeWalk.Visitor):
    container = set
    __AS__('container = set', 'container', locals=locals(), globals=globals(), frame=__FRAME__, line_no=96)

    def __init__(self, container=None):
        if container is None:
            self.collection = __FC__('self.container()', self.container, locals(), globals(), __FRAME__, 100)
            __AS__('self.collection = self.container()', 'self.collection', locals=locals(), globals=globals(), frame=__FRAME__, line_no=100)
        else:
            self.collection = container
            __AS__('self.collection = container', 'self.collection', locals=locals(), globals=globals(), frame=__FRAME__, line_no=102)

    def done(self):
        return self.collection

class Chart:

    def __init__(self, rows):
        """An Earley chart is a list of rows for every input word"""
        self.rows = rows
        __AS__('self.rows = rows', 'self.rows', locals=locals(), globals=globals(), frame=__FRAME__, line_no=111)

    def __len__(self):
        """Chart length"""
        return __FC__('len(self.rows)', len, locals(), globals(), __FRAME__, 115, self.rows)

    def __repr__(self):
        """Nice string representation"""
        st = '<Chart>\n\t'
        __AS__("st = '<Chart>\n\t'", 'st', locals=locals(), globals=globals(), frame=__FRAME__, line_no=119)
        __iter = self.rows.__iter__()
        while True:
            try:
                r = __iter.__next__()
            except StopIteration:
                break
            st += __FC__('str(r)', str, locals(), globals(), __FRAME__, 122, r) + '\n\t'
        st = __FC__("st.removesuffix('\n\t')", st.removesuffix, locals(), globals(), __FRAME__, 123, '\n\t')
        __AS__("st = st.removesuffix('\n\t')", 'st', locals=locals(), globals=globals(), frame=__FRAME__, line_no=119)
        st += '\n</Chart>'
        return st

    def add_row(self, row):
        """Add a row to chart, only if wasn't already there"""
        if not row in self.rows:
            __FC__('self.rows.append(row)', self.rows.append, locals(), globals(), __FRAME__, 131, row)

class ChartRow:

    def __init__(self, rule, dot=0, start=0, previous=None, completing=None):
        """Initialize a chart row, consisting of a rule, a position
           index inside the rule, index of starting chart and
           pointers to parent rows"""
        self.rule = rule
        __AS__('self.rule = rule', 'self.rule', locals=locals(), globals=globals(), frame=__FRAME__, line_no=139)
        self.dot = dot
        __AS__('self.dot = dot', 'self.dot', locals=locals(), globals=globals(), frame=__FRAME__, line_no=139)
        self.start = start
        __AS__('self.start = start', 'self.start', locals=locals(), globals=globals(), frame=__FRAME__, line_no=139)
        self.completing = completing
        __AS__('self.completing = completing', 'self.completing', locals=locals(), globals=globals(), frame=__FRAME__, line_no=139)
        self.previous = previous
        __AS__('self.previous = previous', 'self.previous', locals=locals(), globals=globals(), frame=__FRAME__, line_no=139)

    def __len__(self):
        """A chart's length is its rule's length"""
        return __FC__('len(self.rule)', len, locals(), globals(), __FRAME__, 147, self.rule)

    def __repr__(self):
        """Nice string representation:
            <Row <LHS -> RHS .> [start]>"""
        rhs = __FC__('list(self.rule.rhs)', list, locals(), globals(), __FRAME__, 152, self.rule.rhs)
        __AS__('rhs = list(self.rule.rhs)', 'rhs', locals=locals(), globals=globals(), frame=__FRAME__, line_no=152)
        __FC__("rhs.insert(self.dot, '.')", rhs.insert, locals(), globals(), __FRAME__, 153, self.dot, '.')
        rule_str = '[{0} -> {1}]'.format(self.rule.lhs, ' '.join(rhs))
        __AS__("rule_str = '[{0} -> {1}]'.format(self.rule.lhs, ' '.join(rhs))", 'rule_str', locals=locals(), globals=globals(), frame=__FRAME__, line_no=152)
        return '<Row {0} [{1}]> completes ({2}) follows ({3})'.format(rule_str, self.start, self.completing, self.previous)

    def __eq__(self, other):
        """Two rows are equal if they share the same rule, start and dot"""
        return __FC__('len(self)', len, locals(), globals(), __FRAME__, 160, self) == __FC__('len(other)', len, locals(), globals(), __FRAME__, 160, other) and self.dot == other.dot and (self.start == other.start) and (self.rule == other.rule)

    def is_complete(self):
        """Returns true if rule was completely parsed, i.e. the dot is at the end"""
        return __FC__('len(self)', len, locals(), globals(), __FRAME__, 172, self) == self.dot

    def next_category(self):
        """Return next category to parse, i.e. the one after the dot"""
        x = __FC__('len(self)', len, locals(), globals(), __FRAME__, 176, self)
        __AS__('x = len(self)', 'x', locals=locals(), globals=globals(), frame=__FRAME__, line_no=176)
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
        __AS__('self.word = word', 'self.word', locals=locals(), globals=globals(), frame=__FRAME__, line_no=191)
        self.tags = tags
        __AS__('self.tags = tags', 'self.tags', locals=locals(), globals=globals(), frame=__FRAME__, line_no=191)

    def __repr__(self):
        """Nice string representation"""
        return '{0}<{1}>'.format(self.word, ','.join(self.tags))

class Sentence:

    def __init__(self, words=[]):
        """A sentence is a list of words"""
        self.words = words
        __AS__('self.words = words', 'self.words', locals=locals(), globals=globals(), frame=__FRAME__, line_no=202)

    def __str__(self):
        """Nice string representation"""
        s = ''
        __AS__("s = ''", 's', locals=locals(), globals=globals(), frame=__FRAME__, line_no=207)
        __iter = self.words.__iter__()
        while True:
            try:
                w = __iter.__next__()
            except StopIteration:
                break
            s += __FC__('str(w)', str, locals(), globals(), __FRAME__, 209, w) + ' '
        return s

    def __len__(self):
        """Sentence's length"""
        return __FC__('len(self.words)', len, locals(), globals(), __FRAME__, 215, self.words)

    def __getitem__(self, index):
        """Return a word of a given index"""
        lx = __FC__('len(self)', len, locals(), globals(), __FRAME__, 219, self)
        __AS__('lx = len(self)', 'lx', locals=locals(), globals=globals(), frame=__FRAME__, line_no=219)
        if index >= 0 and index < lx:
            return self.words[index]
        else:
            return None

    def add_word(self, word):
        """Add word to sentence"""
        __FC__('self.words.append(word)', self.words.append, locals(), globals(), __FRAME__, 227, word)

    @staticmethod
    def from_string(text):
        """Create a Sentence object from a given string in the Apertium
           stream format:
              time/time<N> flies/flies<N>/flies<V> like/like<P>/like<V>
              an/an<D> arrow/arrow<N>"""
        lemmarex = __FC__("re.compile('^[^\\/]*')", re.compile, locals(), globals(), __FRAME__, 238, '^[^\\/]*')
        __AS__("lemmarex = re.compile('^[^\\/]*')", 'lemmarex', locals=locals(), globals=globals(), frame=__FRAME__, line_no=238)
        tagsrex = __FC__("re.compile('\\/[^\\<]*\\<([^\\>]*)\\>')", re.compile, locals(), globals(), __FRAME__, 239, '\\/[^\\<]*\\<([^\\>]*)\\>')
        __AS__("tagsrex = re.compile('\\/[^\\<]*\\<([^\\>]*)\\>')", 'tagsrex', locals=locals(), globals=globals(), frame=__FRAME__, line_no=238)
        sentence = __FC__('Sentence()', Sentence, locals(), globals(), __FRAME__, 241)
        __AS__('sentence = Sentence()', 'sentence', locals=locals(), globals=globals(), frame=__FRAME__, line_no=238)
        words = __FC__('text.strip()', text.strip, locals(), globals(), __FRAME__, 242).split(' ')
        __AS__("words = text.strip().split(' ')", 'words', locals=locals(), globals=globals(), frame=__FRAME__, line_no=238)
        __iter = words.__iter__()
        while True:
            try:
                word = __iter.__next__()
            except StopIteration:
                break
            lemma = __FC__('lemmarex.match(word)', lemmarex.match, locals(), globals(), __FRAME__, 244, word).group(0)
            __AS__('lemma = lemmarex.match(word).group(0)', 'lemma', locals=locals(), globals=globals(), frame=__FRAME__, line_no=244)
            tags = __FC__('tagsrex.findall(word)', tagsrex.findall, locals(), globals(), __FRAME__, 245, word)
            __AS__('tags = tagsrex.findall(word)', 'tags', locals=locals(), globals=globals(), frame=__FRAME__, line_no=244)
            w = __FC__('Word(lemma, tags)', Word, locals(), globals(), __FRAME__, 246, lemma, tags)
            __AS__('w = Word(lemma, tags)', 'w', locals=locals(), globals=globals(), frame=__FRAME__, line_no=244)
            __FC__('sentence.add_word(w)', sentence.add_word, locals(), globals(), __FRAME__, 247, w)
        return sentence

class Tree(object):

    def __init__(self, root, subtrees=None):
        self.root = root
        __AS__('self.root = root', 'self.root', locals=locals(), globals=globals(), frame=__FRAME__, line_no=255)
        if subtrees is None:
            self.subtrees = []
            __AS__('self.subtrees = []', 'self.subtrees', locals=locals(), globals=globals(), frame=__FRAME__, line_no=257)
        else:
            self.subtrees = subtrees
            __AS__('self.subtrees = subtrees', 'self.subtrees', locals=locals(), globals=globals(), frame=__FRAME__, line_no=259)

    def __eq__(self, other):
        if not __FC__('isinstance(other, Tree)', isinstance, locals(), globals(), __FRAME__, 262, other, Tree):
            return NotImplemented
        return __FC__('type(self)', type, locals(), globals(), __FRAME__, 264, self) == __FC__('type(other)', type, locals(), globals(), __FRAME__, 264, other) and (self.root, self.subtrees) == (other.root, other.subtrees)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return __FC__("hash((self.root, __FC__('tuple(self.subtrees)', tuple, locals(), globals(), __FRAME__, 271, self.subtrees)))", hash, locals(), globals(), __FRAME__, 271, (self.root, tuple(self.subtrees)))

    def repr(self, leaf_fmt):
        if self.subtrees:
            subreprs = ', '.join((__FC__('x.repr(leaf_fmt)', x.repr, locals(), globals(), __FRAME__, 275, leaf_fmt) for x in self.subtrees))
            __AS__("subreprs = ', '.join((x.repr(leaf_fmt) for x in self.subtrees))", 'subreprs', locals=locals(), globals=globals(), frame=__FRAME__, line_no=275)
            return '%s{%s}' % (__FC__('leaf_fmt(self.root)', leaf_fmt, locals(), globals(), __FRAME__, 276, self.root), subreprs)
        else:
            return __FC__('leaf_fmt(self.root)', leaf_fmt, locals(), globals(), __FRAME__, 278, self.root)

    def __repr__(self):
        return __FC__('self.repr(repr)', self.repr, locals(), globals(), __FRAME__, 281, repr)

    def __str__(self):
        return __FC__('self.repr(str)', self.repr, locals(), globals(), __FRAME__, 284, str)

    def clone(self):
        return __FC__('self.reconstruct(self)', self.reconstruct, locals(), globals(), __FRAME__, 287, self)

    @classmethod
    def reconstruct(cls, t):
        return __FC__("cls(t.root, [__FC__('cls.reconstruct(s)', cls.reconstruct, locals(), globals(), __FRAME__, 291, s) for s in t.subtrees])", cls, locals(), globals(), __FRAME__, 291, t.root, [cls.reconstruct(s) for s in t.subtrees])

    @property
    def nodes(self):
        return __FC__('list(PreorderWalk(self))', list, locals(), globals(), __FRAME__, 295, PreorderWalk(self))

    @property
    def leaves(self):
        return [n for n in __FC__('PreorderWalk(self)', PreorderWalk, locals(), globals(), __FRAME__, 299, self) if not n.subtrees]

    @property
    def terminals(self):
        """ @return a list of the values located at the leaf nodes. """
        return [n.root for n in self.leaves]

    @property
    def depth(self):
        """ Computes length of longest branch (iterative version). """
        stack = [(0, self)]
        __AS__('stack = [(0, self)]', 'stack', locals=locals(), globals=globals(), frame=__FRAME__, line_no=309)
        max_depth = 0
        __AS__('max_depth = 0', 'max_depth', locals=locals(), globals=globals(), frame=__FRAME__, line_no=309)
        while stack:
            (depth, top) = stack[0]
            __AS__('(depth, top) = stack[0]', 'top', locals=locals(), globals=globals(), frame=__FRAME__, line_no=312)
            __AS__('(depth, top) = stack[0]', 'depth', locals=locals(), globals=globals(), frame=__FRAME__, line_no=312)
            max_depth = __FC__('max(depth, max_depth)', max, locals(), globals(), __FRAME__, 313, depth, max_depth)
            __AS__('max_depth = max(depth, max_depth)', 'max_depth', locals=locals(), globals=globals(), frame=__FRAME__, line_no=312)
            stack[:1] = [(depth + 1, x) for x in top.subtrees]
            __AS__('stack[:1] = [(depth + 1, x) for x in top.subtrees]', 'stack[:1:]', locals=locals(), globals=globals(), frame=__FRAME__, line_no=312)
        return max_depth

    def split(self, separator=None):
        if separator is None:
            separator = self.root
            __AS__('separator = self.root', 'separator', locals=locals(), globals=globals(), frame=__FRAME__, line_no=318)
        if self.root == separator:
            return [item for s in self.subtrees for item in __FC__('s.split(separator)', s.split, locals(), globals(), __FRAME__, 320, separator)]
        else:
            return [self]

    def fold(self):
        return __FC__('type(self)(self.root, self.split())', type(self), locals(), globals(), __FRAME__, 325, self.root, self.split())

def pretty(expr: Tree, parent: Tuple[str, int]=('.', 0), follow: str='') -> str:
    if expr.root in ['id', 'num']:
        return expr.subtrees[0].root
    if expr.root == '\\':
        tmpl = '\\%s. %s'
        __AS__("tmpl = '\\%s. %s'", 'tmpl', locals=locals(), globals=globals(), frame=__FRAME__, line_no=331)
        if parent == ('@', 0) or parent[0] == follow == '@':
            tmpl = '(%s)' % tmpl
            __AS__("tmpl = '(%s)' % tmpl", 'tmpl', locals=locals(), globals=globals(), frame=__FRAME__, line_no=333)
    elif expr.root == '@':
        tmpl = '%s %s'
        __AS__("tmpl = '%s %s'", 'tmpl', locals=locals(), globals=globals(), frame=__FRAME__, line_no=335)
        if parent == ('@', 1):
            tmpl = '(%s)' % tmpl
            __AS__("tmpl = '(%s)' % tmpl", 'tmpl', locals=locals(), globals=globals(), frame=__FRAME__, line_no=337)
    else:
        return __FC__('str(expr)', str, locals(), globals(), __FRAME__, 339, expr)
    n = __FC__('len(expr.subtrees)', len, locals(), globals(), __FRAME__, 341, expr.subtrees)
    __AS__('n = len(expr.subtrees)', 'n', locals=locals(), globals=globals(), frame=__FRAME__, line_no=341)
    return tmpl % __FC__("tuple((__FC__('pretty(s, (expr.root, i), expr.root if i < n - 1 else follow)', pretty, locals(), globals(), __FRAME__, 342, s, (expr.root, i), expr.root if i < n - 1 else follow) for (i, s) in __FC__('enumerate(expr.subtrees)', enumerate, locals(), globals(), __FRAME__, 343, expr.subtrees)))", tuple, locals(), globals(), __FRAME__, 342, (pretty(s, (expr.root, i), expr.root if i < n - 1 else follow) for (i, s) in enumerate(expr.subtrees)))

class ParseTrees:

    def __init__(self, parser):
        """Initialize a syntax tree parsing process"""
        self.parser = parser
        __AS__('self.parser = parser', 'self.parser', locals=locals(), globals=globals(), frame=__FRAME__, line_no=350)
        self.charts = parser.charts
        __AS__('self.charts = parser.charts', 'self.charts', locals=locals(), globals=globals(), frame=__FRAME__, line_no=350)
        self.length = __FC__('len(parser)', len, locals(), globals(), __FRAME__, 352, parser)
        __AS__('self.length = len(parser)', 'self.length', locals=locals(), globals=globals(), frame=__FRAME__, line_no=350)
        self.nodes = []
        __AS__('self.nodes = []', 'self.nodes', locals=locals(), globals=globals(), frame=__FRAME__, line_no=350)
        __iter = parser.complete_parses.__iter__()
        while True:
            try:
                root = __iter.__next__()
            except StopIteration:
                break
            __FC__('self.nodes.extend(self.build_nodes(root))', self.nodes.extend, locals(), globals(), __FRAME__, 356, self.build_nodes(root))

    def __len__(self):
        """Trees count"""
        return __FC__('len(self.nodes)', len, locals(), globals(), __FRAME__, 360, self.nodes)

    def __repr__(self):
        """String representation of a list of trees with indexes"""
        return '<Parse Trees>\n{0}</Parse Trees>'.format('\n'.join(('Parse tree #{0}:\n{1}\n\n'.format(i + 1, __FC__('str(self.nodes[i])', str, locals(), globals(), __FRAME__, 366, self.nodes[i])) for i in __FC__('range(len(self))', range, locals(), globals(), __FRAME__, 367, len(self)))))

    def build_nodes(self, root):
        """Recursively create subtree for given parse chart row"""
        if root.completing:
            down = __FC__('self.build_nodes(root.completing)', self.build_nodes, locals(), globals(), __FRAME__, 373, root.completing)
            __AS__('down = self.build_nodes(root.completing)', 'down', locals=locals(), globals=globals(), frame=__FRAME__, line_no=373)
        elif root.dot > 0:
            down = [__FC__('Tree(root.prev_category())', Tree, locals(), globals(), __FRAME__, 375, root.prev_category())]
            __AS__('down = [Tree(root.prev_category())]', 'down', locals=locals(), globals=globals(), frame=__FRAME__, line_no=375)
        else:
            down = []
            __AS__('down = []', 'down', locals=locals(), globals=globals(), frame=__FRAME__, line_no=377)
        prev = root.previous
        __AS__('prev = root.previous', 'prev', locals=locals(), globals=globals(), frame=__FRAME__, line_no=380)
        left = []
        __AS__('left = []', 'left', locals=locals(), globals=globals(), frame=__FRAME__, line_no=380)
        if prev:
            left[:0] = [x.subtrees for x in __FC__('self.build_nodes(prev)', self.build_nodes, locals(), globals(), __FRAME__, 383, prev)]
            __AS__('left[:0] = [x.subtrees for x in self.build_nodes(prev)]', 'left[::]', locals=locals(), globals=globals(), frame=__FRAME__, line_no=383)
            prev = prev.previous
            __AS__('prev = prev.previous', 'prev', locals=locals(), globals=globals(), frame=__FRAME__, line_no=383)
        else:
            left = [[]]
            __AS__('left = [[]]', 'left', locals=locals(), globals=globals(), frame=__FRAME__, line_no=386)
        __iter = left.__iter__()
        while True:
            try:
                x = __iter.__next__()
            except StopIteration:
                break
            __FC__('x.extend(down)', x.extend, locals(), globals(), __FRAME__, 389, down)
        return [__FC__('Tree(root.rule.lhs, subtrees)', Tree, locals(), globals(), __FRAME__, 391, root.rule.lhs, subtrees) for subtrees in left]

class Parser:
    GAMMA_SYMBOL = 'γ'
    __AS__("GAMMA_SYMBOL = 'γ'", 'GAMMA_SYMBOL', locals=locals(), globals=globals(), frame=__FRAME__, line_no=395)

    def __init__(self, grammar, sentence, debug=False):
        """Initialize parser with grammar and sentence"""
        self.grammar = grammar
        __AS__('self.grammar = grammar', 'self.grammar', locals=locals(), globals=globals(), frame=__FRAME__, line_no=399)
        self.sentence = sentence if __FC__('isinstance(sentence, Sentence)', isinstance, locals(), globals(), __FRAME__, 400, sentence, Sentence) else __FC__('Sentence(sentence)', Sentence, locals(), globals(), __FRAME__, 400, sentence)
        __AS__('self.sentence = sentence if isinstance(sentence, Sentence) else Sentence(sentence)', 'self.sentence', locals=locals(), globals=globals(), frame=__FRAME__, line_no=399)
        self.debug = debug
        __AS__('self.debug = debug', 'self.debug', locals=locals(), globals=globals(), frame=__FRAME__, line_no=399)
        self.charts = [__FC__('Chart([])', Chart, locals(), globals(), __FRAME__, 404, []) for _ in __FC__("range(__FC__('len(self)', len, locals(), globals(), __FRAME__, 404, self) + 1)", range, locals(), globals(), __FRAME__, 404, len(self) + 1)]
        __AS__('self.charts = [Chart([]) for _ in range(len(self) + 1)]', 'self.charts', locals=locals(), globals=globals(), frame=__FRAME__, line_no=399)
        self.complete_parses = []
        __AS__('self.complete_parses = []', 'self.complete_parses', locals=locals(), globals=globals(), frame=__FRAME__, line_no=399)

    def __len__(self):
        """Length of input sentence"""
        return __FC__('len(self.sentence)', len, locals(), globals(), __FRAME__, 409, self.sentence)

    def init_first_chart(self):
        """Add initial Gamma rule to first chart"""
        row = __FC__("ChartRow(Rule(Parser.GAMMA_SYMBOL, [self.grammar.start_symbol or 'S']), 0, 0)", ChartRow, locals(), globals(), __FRAME__, 413, Rule(Parser.GAMMA_SYMBOL, [self.grammar.start_symbol or 'S']), 0, 0)
        __AS__("row = ChartRow(Rule(Parser.GAMMA_SYMBOL, [self.grammar.start_symbol or 'S']), 0, 0)", 'row', locals=locals(), globals=globals(), frame=__FRAME__, line_no=413)
        self.charts[0].add_row(row)

    def prescan(self, chart, position):
        """Scan current word in sentence, and add appropriate
           grammar categories to current chart"""
        word = self.sentence[position - 1]
        __AS__('word = self.sentence[position - 1]', 'word', locals=locals(), globals=globals(), frame=__FRAME__, line_no=419)
        if word:
            rules = [__FC__('Rule(tag, [word.word])', Rule, locals(), globals(), __FRAME__, 421, tag, [word.word]) for tag in word.tags]
            __AS__('rules = [Rule(tag, [word.word]) for tag in word.tags]', 'rules', locals=locals(), globals=globals(), frame=__FRAME__, line_no=421)
            __iter = rules.__iter__()
            while True:
                try:
                    rule = __iter.__next__()
                except StopIteration:
                    break
                __FC__('chart.add_row(ChartRow(rule, 1, position - 1))', chart.add_row, locals(), globals(), __FRAME__, 423, ChartRow(rule, 1, position - 1))

    def predict(self, chart, position):
        """Predict next parse by looking up grammar rules
           for pending categories in current chart"""
        __iter = chart.rows.__iter__()
        while True:
            try:
                row = __iter.__next__()
            except StopIteration:
                break
            next_cat = __FC__('row.next_category()', row.next_category, locals(), globals(), __FRAME__, 429)
            __AS__('next_cat = row.next_category()', 'next_cat', locals=locals(), globals=globals(), frame=__FRAME__, line_no=429)
            rules = self.grammar[next_cat]
            __AS__('rules = self.grammar[next_cat]', 'rules', locals=locals(), globals=globals(), frame=__FRAME__, line_no=429)
            if rules:
                for rule in rules:
                    new = __FC__('ChartRow(rule, 0, position)', ChartRow, locals(), globals(), __FRAME__, 433, rule, 0, position)
                    __AS__('new = ChartRow(rule, 0, position)', 'new', locals=locals(), globals=globals(), frame=__FRAME__, line_no=433)
                    __FC__('chart.add_row(new)', chart.add_row, locals(), globals(), __FRAME__, 434, new)

    def complete(self, chart, position):
        """Complete a rule that was done parsing, and
           promote previously pending rules"""
        __iter = chart.rows.__iter__()
        while True:
            try:
                row = __iter.__next__()
            except StopIteration:
                break
            if __FC__('row.is_complete()', row.is_complete, locals(), globals(), __FRAME__, 440):
                completed = row.rule.lhs
                __AS__('completed = row.rule.lhs', 'completed', locals=locals(), globals=globals(), frame=__FRAME__, line_no=441)
                for r in self.charts[row.start].rows:
                    if completed == __FC__('r.next_category()', r.next_category, locals(), globals(), __FRAME__, 443):
                        new = __FC__('ChartRow(r.rule, r.dot + 1, r.start, r, row)', ChartRow, locals(), globals(), __FRAME__, 444, r.rule, r.dot + 1, r.start, r, row)
                        __AS__('new = ChartRow(r.rule, r.dot + 1, r.start, r, row)', 'new', locals=locals(), globals=globals(), frame=__FRAME__, line_no=444)
                        __FC__('chart.add_row(new)', chart.add_row, locals(), globals(), __FRAME__, 445, new)

    def parse(self):
        """Main Earley's Parser loop"""
        __FC__('self.init_first_chart()', self.init_first_chart, locals(), globals(), __FRAME__, 449)
        i = 0
        __AS__('i = 0', 'i', locals=locals(), globals=globals(), frame=__FRAME__, line_no=451)
        while i < __FC__('len(self.charts)', len, locals(), globals(), __FRAME__, 453, self.charts):
            chart = self.charts[i]
            __AS__('chart = self.charts[i]', 'chart', locals=locals(), globals=globals(), frame=__FRAME__, line_no=454)
            __FC__('self.prescan(chart, i)', self.prescan, locals(), globals(), __FRAME__, 455, chart, i)
            length = __FC__('len(chart)', len, locals(), globals(), __FRAME__, 459, chart)
            __AS__('length = len(chart)', 'length', locals=locals(), globals=globals(), frame=__FRAME__, line_no=454)
            old_length = -1
            __AS__('old_length = -1', 'old_length', locals=locals(), globals=globals(), frame=__FRAME__, line_no=454)
            while old_length != length:
                __FC__('self.predict(chart, i)', self.predict, locals(), globals(), __FRAME__, 462, chart, i)
                __FC__('self.complete(chart, i)', self.complete, locals(), globals(), __FRAME__, 463, chart, i)
                old_length = length
                __AS__('old_length = length', 'old_length', locals=locals(), globals=globals(), frame=__FRAME__, line_no=465)
                length = __FC__('len(chart)', len, locals(), globals(), __FRAME__, 466, chart)
                __AS__('length = len(chart)', 'length', locals=locals(), globals=globals(), frame=__FRAME__, line_no=465)
            i += 1
        if self.debug:
            __FC__("print('Parsing charts:')", print, locals(), globals(), __FRAME__, 472, 'Parsing charts:')
            __iter = __FC__('range(len(self.charts))', range, locals(), globals(), __FRAME__, 473, len(self.charts)).__iter__()
            while True:
                try:
                    i = __iter.__next__()
                except StopIteration:
                    break
                __FC__("print('-----------{0}-------------'.format(i))", print, locals(), globals(), __FRAME__, 474, '-----------{0}-------------'.format(i))
                __FC__('print(self.charts[i])', print, locals(), globals(), __FRAME__, 475, self.charts[i])
                __FC__("print('-------------------------'.format(i))", print, locals(), globals(), __FRAME__, 476, '-------------------------'.format(i))

    def is_valid_sentence(self):
        """Returns true if sentence has a complete parse tree"""
        res = False
        __AS__('res = False', 'res', locals=locals(), globals=globals(), frame=__FRAME__, line_no=480)
        __iter = self.charts[-1].rows.__iter__()
        while True:
            try:
                row = __iter.__next__()
            except StopIteration:
                break
            if row.start == 0:
                if row.rule.lhs == self.GAMMA_SYMBOL:
                    if __FC__('row.is_complete()', row.is_complete, locals(), globals(), __FRAME__, 484):
                        __FC__('self.complete_parses.append(row)', self.complete_parses.append, locals(), globals(), __FRAME__, 485, row)
                        res = True
                        __AS__('res = True', 'res', locals=locals(), globals=globals(), frame=__FRAME__, line_no=486)
        return res

class Rule:

    def __init__(self, lhs, rhs):
        """Initializes grammar rule: LHS -> [RHS]"""
        self.lhs = lhs
        __AS__('self.lhs = lhs', 'self.lhs', locals=locals(), globals=globals(), frame=__FRAME__, line_no=493)
        self.rhs = rhs
        __AS__('self.rhs = rhs', 'self.rhs', locals=locals(), globals=globals(), frame=__FRAME__, line_no=493)

    def __len__(self):
        """A rule's length is its RHS's length"""
        return __FC__('len(self.rhs)', len, locals(), globals(), __FRAME__, 498, self.rhs)

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
        __AS__('self.rules = {}', 'self.rules', locals=locals(), globals=globals(), frame=__FRAME__, line_no=519)
        self.start_symbol = None
        __AS__('self.start_symbol = None', 'self.start_symbol', locals=locals(), globals=globals(), frame=__FRAME__, line_no=519)

    def __repr__(self):
        """Nice string representation"""
        st = '<Grammar>\n'
        __AS__("st = '<Grammar>\n'", 'st', locals=locals(), globals=globals(), frame=__FRAME__, line_no=524)
        __iter = __FC__('self.rules.values()', self.rules.values, locals(), globals(), __FRAME__, 525).__iter__()
        while True:
            try:
                group = __iter.__next__()
            except StopIteration:
                break
            for rule in group:
                st += '\t{0}\n'.format(__FC__('str(rule)', str, locals(), globals(), __FRAME__, 527, rule))
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
        __AS__('lhs = rule.lhs', 'lhs', locals=locals(), globals=globals(), frame=__FRAME__, line_no=540)
        if lhs in self.rules:
            self.rules[lhs].append(rule)
        else:
            d = self.rules
            __AS__('d = self.rules', 'd', locals=locals(), globals=globals(), frame=__FRAME__, line_no=545)
            d[lhs] = [rule]
            __AS__('d[lhs] = [rule]', 'd[lhs:1]', locals=locals(), globals=globals(), frame=__FRAME__, line_no=545)
        if self.start_symbol is None:
            self.start_symbol = lhs
            __AS__('self.start_symbol = lhs', 'self.start_symbol', locals=locals(), globals=globals(), frame=__FRAME__, line_no=549)

    @staticmethod
    def from_file(filename):
        """Returns a Grammar instance created from a text file.
        """
        return __FC__('Grammar.from_lines(open(filename))', Grammar.from_lines, locals(), globals(), __FRAME__, 555, open(filename))

    @staticmethod
    def from_string(string):
        """Returns a Grammar instance created from a string.
        """
        return __FC__('Grammar.from_lines(string.splitlines())', Grammar.from_lines, locals(), globals(), __FRAME__, 561, string.splitlines())

    @staticmethod
    def from_lines(iterable):
        """Returns a Grammar instance created from an iterator over lines.
           The lines should have the format:
               lhs -> outcome | outcome | outcome"""
        grammar = __FC__('Grammar()', Grammar, locals(), globals(), __FRAME__, 569)
        __AS__('grammar = Grammar()', 'grammar', locals=locals(), globals=globals(), frame=__FRAME__, line_no=569)
        __iter = iterable.__iter__()
        while True:
            try:
                line = __iter.__next__()
            except StopIteration:
                break
            comm = __FC__("line.find('#')", line.find, locals(), globals(), __FRAME__, 572, '#')
            __AS__("comm = line.find('#')", 'comm', locals=locals(), globals=globals(), frame=__FRAME__, line_no=572)
            if comm >= 0:
                line = line[:comm]
                __AS__('line = line[:comm]', 'line', locals=locals(), globals=globals(), frame=__FRAME__, line_no=574)
            line = __FC__('line.strip()', line.strip, locals(), globals(), __FRAME__, 576)
            __AS__('line = line.strip()', 'line', locals=locals(), globals=globals(), frame=__FRAME__, line_no=572)
            if line == '':
                continue
            rule = __FC__("line.split('->', 1)", line.split, locals(), globals(), __FRAME__, 580, '->', 1)
            __AS__("rule = line.split('->', 1)", 'rule', locals=locals(), globals=globals(), frame=__FRAME__, line_no=572)
            if __FC__('len(rule)', len, locals(), globals(), __FRAME__, 581, rule) != 2:
                raise ValueError("invalid grammar format: '%s'" % line)
            lhs = rule[0].strip()
            __AS__('lhs = rule[0].strip()', 'lhs', locals=locals(), globals=globals(), frame=__FRAME__, line_no=572)
            for outcome in rule[1].split('|'):
                rhs = outcome.strip()
                __AS__('rhs = outcome.strip()', 'rhs', locals=locals(), globals=globals(), frame=__FRAME__, line_no=585)
                symbols = rhs.split(' ') if rhs else []
                __AS__("symbols = rhs.split(' ') if rhs else []", 'symbols', locals=locals(), globals=globals(), frame=__FRAME__, line_no=585)
                r = Rule(lhs, symbols)
                __AS__('r = Rule(lhs, symbols)', 'r', locals=locals(), globals=globals(), frame=__FRAME__, line_no=585)
                grammar.add_rule(r)
        return grammar

class SillyLexer(object):
    TEXT = 1
    __AS__('TEXT = 1', 'TEXT', locals=locals(), globals=globals(), frame=__FRAME__, line_no=594)
    TOKEN = 2
    __AS__('TOKEN = 2', 'TOKEN', locals=locals(), globals=globals(), frame=__FRAME__, line_no=594)

    def __init__(self, token_regexp):
        if not isinstance(token_regexp, str):
            if isinstance(token_regexp, Iterable):
                token_regexp = '|'.join(token_regexp)
                __AS__("token_regexp = '|'.join(token_regexp)", 'token_regexp', locals=locals(), globals=globals(), frame=__FRAME__, line_no=600)
            else:
                raise ValueError('invalid token specification')
        self.token_re = re.compile(token_regexp)
        __AS__('self.token_re = re.compile(token_regexp)', 'self.token_re', locals=locals(), globals=globals(), frame=__FRAME__, line_no=603)

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
        __AS__('pos = 0', 'pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=611)
        __iter = self.token_re.finditer(input_text).__iter__()
        while True:
            try:
                mo = __iter.__next__()
            except StopIteration:
                break
            (from_, to) = mo.span()
            __AS__('(from_, to) = mo.span()', 'to', locals=locals(), globals=globals(), frame=__FRAME__, line_no=614)
            __AS__('(from_, to) = mo.span()', 'from_', locals=locals(), globals=globals(), frame=__FRAME__, line_no=614)
            if from_ > pos:
                yield (self.TEXT, input_text[from_:pos])
            yield (self.TOKEN, self.mktoken(mo))
            pos = to
            __AS__('pos = to', 'pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=614)

    def mktoken(self, mo):
        return Word(mo.group(), [mo.lastgroup or mo.group()])

class SillyBlocker(object):

    def __init__(self, open_token, close_token):
        self.topen = open_token
        __AS__('self.topen = open_token', 'self.topen', locals=locals(), globals=globals(), frame=__FRAME__, line_no=627)
        self.tclose = close_token
        __AS__('self.tclose = close_token', 'self.tclose', locals=locals(), globals=globals(), frame=__FRAME__, line_no=627)

    def __call__(self, token_stream):
        bal = 0
        __AS__('bal = 0', 'bal', locals=locals(), globals=globals(), frame=__FRAME__, line_no=631)
        (topen, tclose) = (self.topen, self.tclose)
        __AS__('(topen, tclose) = (self.topen, self.tclose)', 'tclose', locals=locals(), globals=globals(), frame=__FRAME__, line_no=631)
        __AS__('(topen, tclose) = (self.topen, self.tclose)', 'topen', locals=locals(), globals=globals(), frame=__FRAME__, line_no=631)
        bag = []
        __AS__('bag = []', 'bag', locals=locals(), globals=globals(), frame=__FRAME__, line_no=631)
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
                __AS__('bag = []', 'bag', locals=locals(), globals=globals(), frame=__FRAME__, line_no=642)
        if bal != 0:
            raise SyntaxError("unbalanced '%s' and '%s'" % (self.topen, self.tclose))

def PaladinSkipStatement(args):
    pass

class LambdaParser(object):
    TOKENS = '(let|in)(?![\\w\\d_])   (?P<id>[^\\W\\d]\\w*)   (?P<num>\\d+)   [\\\\.()=]'.split()
    __AS__("TOKENS = '(let|in)(?![\\w\\d_])   (?P<id>[^\\W\\d]\\w*)   (?P<num>\\d+)   [\\\\.()=]'.split()", 'TOKENS', locals=locals(), globals=globals(), frame=__FRAME__, line_no=653)
    GRAMMAR = '\n    E    ->  \\. | let_    |   E1  |  E1λ\n    E1   ->  @            |   E0\n    E1λ  ->  @λ           |   E0\n    E0   ->  id | num     |  ( E )\n    \\.   ->  \\ L . E \n    @    ->  E1 E0\n    @λ   ->  E1 \\.\n    L    ->  id L |\n    let_ ->  let id = E in E\n    '
    __AS__("GRAMMAR = '\n    E    ->  \\. | let_    |   E1  |  E1λ\n    E1   ->  @            |   E0\n    E1λ  ->  @λ           |   E0\n    E0   ->  id | num     |  ( E )\n    \\.   ->  \\ L . E \n    @    ->  E1 E0\n    @λ   ->  E1 \\.\n    L    ->  id L |\n    let_ ->  let id = E in E\n    '", 'GRAMMAR', locals=locals(), globals=globals(), frame=__FRAME__, line_no=653)

    def __init__(self):
        self.tokenizer = SillyLexer(self.TOKENS)
        __AS__('self.tokenizer = SillyLexer(self.TOKENS)', 'self.tokenizer', locals=locals(), globals=globals(), frame=__FRAME__, line_no=668)
        self.grammar = Grammar.from_string(self.GRAMMAR)
        __AS__('self.grammar = Grammar.from_string(self.GRAMMAR)', 'self.grammar', locals=locals(), globals=globals(), frame=__FRAME__, line_no=668)

    def __call__(self, program_text: str) -> Optional[Tree]:
        tokens = list(self.tokenizer(program_text))
        __AS__('tokens = list(self.tokenizer(program_text))', 'tokens', locals=locals(), globals=globals(), frame=__FRAME__, line_no=672)
        earley = Parser(grammar=self.grammar, sentence=tokens, debug=False)
        __AS__('earley = Parser(grammar=self.grammar, sentence=tokens, debug=False)', 'earley', locals=locals(), globals=globals(), frame=__FRAME__, line_no=672)
        earley.parse()
        if earley.is_valid_sentence():
            trees = ParseTrees(earley)
            __AS__('trees = ParseTrees(earley)', 'trees', locals=locals(), globals=globals(), frame=__FRAME__, line_no=678)
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
            __AS__('args = t.subtrees[1].split()', 'args', locals=locals(), globals=globals(), frame=__FRAME__, line_no=690)
            t = reduce(lambda t, a: Tree('\\', [a, t]), reversed(args), t.subtrees[3])
            __AS__("t = reduce(lambda t, a: Tree('\\', [a, t]), reversed(args), t.subtrees[3])", 't', locals=locals(), globals=globals(), frame=__FRAME__, line_no=690)
        elif t.root == "@'":
            t = Tree('@', t.subtrees)
            __AS__("t = Tree('@', t.subtrees)", 't', locals=locals(), globals=globals(), frame=__FRAME__, line_no=693)
        elif t.root == 'L':
            t = Tree('.', t.split())
            __AS__("t = Tree('.', t.split())", 't', locals=locals(), globals=globals(), frame=__FRAME__, line_no=695)
        return Tree(t.root, [self.postprocess(s) for s in t.subtrees])

class LambdaInterpreter(object):

    def __init__(self, options=None):
        self.options = options or LambdaInterpreter.Options()
        __AS__('self.options = options or LambdaInterpreter.Options()', 'self.options', locals=locals(), globals=globals(), frame=__FRAME__, line_no=703)

    def __call__(self, expr):
        return self.normal_form(self.preprocess(expr))

    def preprocess(self, expr):
        if expr.root == 'num':
            return self.church_numeral(int(expr.subtrees[0].root))
        elif expr.root == 'let_':
            T = type(expr)
            __AS__('T = type(expr)', 'T', locals=locals(), globals=globals(), frame=__FRAME__, line_no=712)
            (var, defn, body) = (expr.subtrees[1], expr.subtrees[3], expr.subtrees[5])
            __AS__('(var, defn, body) = (expr.subtrees[1], expr.subtrees[3], expr.subtrees[5])', 'body', locals=locals(), globals=globals(), frame=__FRAME__, line_no=712)
            __AS__('(var, defn, body) = (expr.subtrees[1], expr.subtrees[3], expr.subtrees[5])', 'defn', locals=locals(), globals=globals(), frame=__FRAME__, line_no=712)
            __AS__('(var, defn, body) = (expr.subtrees[1], expr.subtrees[3], expr.subtrees[5])', 'var', locals=locals(), globals=globals(), frame=__FRAME__, line_no=712)
            return self.preprocess(T('@', [T('\\', [var, body]), defn]))
        else:
            return type(expr)(expr.root, [self.preprocess(s) for s in expr.subtrees])

    def normal_form(self, expr):
        print(pretty(expr))
        t = self.options.trace
        __AS__('t = self.options.trace', 't', locals=locals(), globals=globals(), frame=__FRAME__, line_no=720)
        expr = Tree('.', [expr])
        __AS__("expr = Tree('.', [expr])", 'expr', locals=locals(), globals=globals(), frame=__FRAME__, line_no=720)
        while True:
            __iter = PreorderWalk(expr).__iter__()
            while True:
                try:
                    n = __iter.__next__()
                except StopIteration:
                    break
                for (i, s) in enumerate(n.subtrees):
                    if s.root == '@' and s.subtrees[0].root == '\\':
                        n.subtrees[i] = self.beta_reduce(s)
                        __AS__('n.subtrees[i] = self.beta_reduce(s)', 'n.subtrees[i:1]', locals=locals(), globals=globals(), frame=__FRAME__, line_no=726)
                        break
                else:
                    continue
                break
            if t:
                print(' ->', pretty(expr.subtrees[0]))
        if not t:
            print(' ->', pretty(expr.subtrees[0]))
        return expr.subtrees[0]

    def freevars(self, expr):
        if expr.root == 'id':
            return set([expr.subtrees[0].root])
        elif expr.root == '\\':
            return self.freevars(expr.subtrees[1]) - self.freevars(expr.subtrees[0])
        else:
            return reduce(lambda x, y: x | y, map(self.freevars, expr.subtrees), set())

    def beta_reduce(self, redex):
        assert redex.root == '@' and redex.subtrees[0].root == '\\'
        (var, body) = redex.subtrees[0].subtrees
        __AS__('(var, body) = redex.subtrees[0].subtrees', 'body', locals=locals(), globals=globals(), frame=__FRAME__, line_no=749)
        __AS__('(var, body) = redex.subtrees[0].subtrees', 'var', locals=locals(), globals=globals(), frame=__FRAME__, line_no=749)
        arg = redex.subtrees[1]
        __AS__('arg = redex.subtrees[1]', 'arg', locals=locals(), globals=globals(), frame=__FRAME__, line_no=749)
        return self.subst(body, var, arg, fv=self.freevars(arg))

    def subst(self, in_, what, with_, fv=set()):
        if in_ == what:
            return with_.clone()
        elif in_.root == '\\':
            if what == in_.subtrees[0]:
                return in_.clone()
            if in_.subtrees[0].root == 'id' and in_.subtrees[0].subtrees[0].root in fv:
                in_ = self.alpha_rename(in_, fv)
                __AS__('in_ = self.alpha_rename(in_, fv)', 'in_', locals=locals(), globals=globals(), frame=__FRAME__, line_no=760)
            return type(in_)(in_.root, [in_.subtrees[0].clone()] + [self.subst(s, what, with_, fv) for s in in_.subtrees[1:]])
        else:
            return type(in_)(in_.root, [self.subst(s, what, with_, fv) for s in in_.subtrees])

    def alpha_rename(self, expr, fv):
        assert expr.root == '\\' and expr.subtrees[0].root == 'id'
        forbid = fv | set(expr.terminals)
        __AS__('forbid = fv | set(expr.terminals)', 'forbid', locals=locals(), globals=globals(), frame=__FRAME__, line_no=768)
        var = expr.subtrees[0]
        __AS__('var = expr.subtrees[0]', 'var', locals=locals(), globals=globals(), frame=__FRAME__, line_no=768)
        (base, i) = (var.subtrees[0].root, 0)
        __AS__('(base, i) = (var.subtrees[0].root, 0)', 'i', locals=locals(), globals=globals(), frame=__FRAME__, line_no=768)
        __AS__('(base, i) = (var.subtrees[0].root, 0)', 'base', locals=locals(), globals=globals(), frame=__FRAME__, line_no=768)
        while base and base[-1].isdigit():
            base = base[:-1]
            __AS__('base = base[:-1]', 'base', locals=locals(), globals=globals(), frame=__FRAME__, line_no=771)
        if not base:
            base = 'v'
            __AS__("base = 'v'", 'base', locals=locals(), globals=globals(), frame=__FRAME__, line_no=772)
        while '%s%d' % (base, i) in forbid:
            i += 1
        new_var = Tree('id', [Tree('%s%d' % (base, i))])
        __AS__("new_var = Tree('id', [Tree('%s%d' % (base, i))])", 'new_var', locals=locals(), globals=globals(), frame=__FRAME__, line_no=768)
        return self.subst(expr, var, new_var)

    def church_numeral(self, n):
        f = Tree('id', [Tree('f')])
        __AS__("f = Tree('id', [Tree('f')])", 'f', locals=locals(), globals=globals(), frame=__FRAME__, line_no=778)
        x = Tree('id', [Tree('x')])
        __AS__("x = Tree('id', [Tree('x')])", 'x', locals=locals(), globals=globals(), frame=__FRAME__, line_no=778)
        return Tree('\\', [f, Tree('\\', [x, reduce(lambda x, _: Tree('@', [f, x]), range(n), x)])])
    Options = namedtuple('LambdaOptions', ['trace'], defaults=[True])
    __AS__("Options = namedtuple('LambdaOptions', ['trace'], defaults=[True])", 'Options', locals=locals(), globals=globals(), frame=__FRAME__, line_no=782)

class PostorderWalkNoLambdas(TreeWalk):

    def __iter__(self):
        (DOWN, UP) = (0, 1)
        __AS__('(DOWN, UP) = (0, 1)', 'UP', locals=locals(), globals=globals(), frame=__FRAME__, line_no=788)
        __AS__('(DOWN, UP) = (0, 1)', 'DOWN', locals=locals(), globals=globals(), frame=__FRAME__, line_no=788)
        stack = [(DOWN, self.tree)]
        __AS__('stack = [(DOWN, self.tree)]', 'stack', locals=locals(), globals=globals(), frame=__FRAME__, line_no=788)
        while stack:
            (direction, top) = stack.pop()
            __AS__('(direction, top) = stack.pop()', 'top', locals=locals(), globals=globals(), frame=__FRAME__, line_no=791)
            __AS__('(direction, top) = stack.pop()', 'direction', locals=locals(), globals=globals(), frame=__FRAME__, line_no=791)
            if direction == UP:
                yield top
            else:
                stack += [(UP, top)] + ([] if top.root == '\\' else [(DOWN, x) for x in top.subtrees])
if __name__ == '__main__':
    try:
        import argparse
        p = argparse.ArgumentParser()
        __AS__('p = argparse.ArgumentParser()', 'p', locals=locals(), globals=globals(), frame=__FRAME__, line_no=803)
        p.add_argument('n', metavar='N', type=int, nargs='?', default=3, help='(demo) argument to pass to `fact`')
        p.add_argument('--no-trace', action='store_true', default=False, help='disable printing of the derivation; only normal form')
        o = p.parse_args()
        __AS__('o = p.parse_args()', 'o', locals=locals(), globals=globals(), frame=__FRAME__, line_no=803)
        expr = LambdaParser()('\n    let pred = \\n f x. n (\\g h. h (g f)) (\\u. x) (\\u. u) in\n    let Y = \\f. (\\x. f (x x)) (\\x. f (x x)) in\n    let True = \\x y. x in\n    let False = \\x y. y in\n    let is_zero = \\n. n (\\x. False) True in\n    let mult = \\m n f. m (n f) in\n    \n    let fact = Y (\\f n. (is_zero n) 1 (mult n (f (pred n)))) in\n    fact %d\n    ' % 2)
        __AS__("expr = LambdaParser()('\n    let pred = \\n f x. n (\\g h. h (g f)) (\\u. x) (\\u. u) in\n    let Y = \\f. (\\x. f (x x)) (\\x. f (x x)) in\n    let True = \\x y. x in\n    let False = \\x y. y in\n    let is_zero = \\n. n (\\x. False) True in\n    let mult = \\m n f. m (n f) in\n    \n    let fact = Y (\\f n. (is_zero n) 1 (mult n (f (pred n)))) in\n    fact %d\n    ' % 2)", 'expr', locals=locals(), globals=globals(), frame=__FRAME__, line_no=803)
        if expr:
            print('>> Valid expression.')
            print(expr)
            archive.resume_record()
            LambdaInterpreter(LambdaInterpreter.Options(trace=False))(expr)
        else:
            print('>> Invalid expression.')
    finally:
        expressions = [str((rec_key.field, rec_value.rtype.__name__)) for rec_key, rec_values in archive.records.items() for rec_value in rec_values]
        counts = {x: expressions.count(x) for x in set(expressions)}
        plt.xticks(rotation='vertical')
        plt.bar(counts.keys(), counts.values(), color='g')
        plt.yscale('log')
        plt.ylabel('log count')
        plt.tight_layout()
        plt.savefig('/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/test_resources/lab1/src/lambda_calc/semantics_hist.png')


        with open('/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/test_resources/lab1/src/lambda_calc/semantics.csv', 'w+') as fo:
            writer = csv.writer(fo)
            header, rows = archive.to_table()
            writer.writerow(header)
            writer.writerows(rows)

