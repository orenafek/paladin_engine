import re
from functools import reduce
from typing import Optional, Tuple, Iterable


class TreeWalk(object):
    class Visitor(object):
        def visit_node(self, tree_node):
            pass

        def done(self):
            return None

    def __init__(self, tree):
        self.tree = tree

    def __call__(self, visitor):
        for x in self:
            visitor.visit_node(x)
        return visitor.done()

    def __iter__(self):
        raise NotImplementedError


class PreorderWalk(TreeWalk):

    def __iter__(self):
        stack = [self.tree]
        while stack:
            top = stack[0]
            yield top
            stack[:1] = top.subtrees


class PostorderWalk(TreeWalk):

    def __iter__(self):
        DOWN, UP = 0, 1
        stack = [(DOWN, self.tree)]
        while stack:
            direction, top = stack.pop()
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
        SKIP = ('skip',)  # return this from enter() to prune

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

    def __call__(self, tree):
        final = self._traverse(tree)
        return self.visitor.done(tree, final)

    def _traverse(self, tree):
        descend = [1]
        prefix = self.visitor.enter(tree, descend.pop)
        if prefix is self.Visitor.SKIP:
            return prefix
        elif descend:
            infix = self._descend(tree)
        else:
            infix = []
        postfix = self.visitor.leave(tree)
        return self.visitor.join(tree, prefix, infix, postfix)

    def _descend(self, tree):
        return [self._traverse(sub) for sub in tree.subtrees]


class CollectVisitor(RichTreeWalk.Visitor):
    container = set

    def __init__(self, container=None):
        if container is None:
            self.collection = self.container()
        else:
            self.collection = container

    def done(self):
        return self.collection


class Chart:
    def __init__(self, rows):
        """An Earley chart is a list of rows for every input word"""
        self.rows = rows

    def __len__(self):
        """Chart length"""
        return len(self.rows)

    def __repr__(self):
        """Nice string representation"""
        st = '<Chart>\n\t'
        # st += '\n\t'.join(str(r) for r in self.rows)
        for r in self.rows:
            st += str(r) + '\n\t'
        st = st.removesuffix('\n\t')

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
        self.dot = dot
        self.start = start
        self.completing = completing
        self.previous = previous

    def __len__(self):
        """A chart's length is its rule's length"""
        return len(self.rule)

    def __repr__(self):
        """Nice string representation:
            <Row <LHS -> RHS .> [start]>"""
        rhs = list(self.rule.rhs)
        rhs.insert(self.dot, '.')
        rule_str = "[{0} -> {1}]".format(self.rule.lhs, ' '.join(rhs))
        return "<Row {0} [{1}]> completes ({2}) follows ({3})".format(rule_str, self.start, self.completing,
                                                                      self.previous)

    def __eq__(self, other):
        """Two rows are equal if they share the same rule, start and dot"""
        return len(self) == len(other) and \
               self.dot == other.dot and self.start == other.start and self.rule == other.rule
        # if len(self) == len(other):
        #     if self.dot == other.dot:
        #         if self.start == other.start:
        #             if self.rule == other.rule:
        #                 return True
        # return False

    # TODO: BUGGGGG !!!!!!!!!!!
    def is_complete(self):
        """Returns true if rule was completely parsed, i.e. the dot is at the end"""
        return len(self) -1 == self.dot

    def next_category(self):
        """Return next category to parse, i.e. the one after the dot"""
        x = len(self)
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
        self.tags = tags

    def __repr__(self):
        """Nice string representation"""
        return "{0}<{1}>".format(self.word, ','.join(self.tags))


class Sentence:
    def __init__(self, words=[]):
        """A sentence is a list of words"""
        self.words = words

    def __str__(self):
        """Nice string representation"""
        #return ' '.join(str(w) for w in self.words)
        s = ''
        for w in self.words:
            s += str(w) + ' '

        return s

    def __len__(self):
        """Sentence's length"""
        return len(self.words)

    def __getitem__(self, index):
        """Return a word of a given index"""
        lx = len(self)
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
        # TODO handle Apertium format's beginning ^ and ending $ symbols

        # prepare regular expressions to find word and tags
        lemmarex = re.compile('^[^\/]*')
        tagsrex = re.compile('\/[^\<]*\<([^\>]*)\>')

        sentence = Sentence()
        words = text.strip().split(' ')
        for word in words:
            lemma = lemmarex.match(word).group(0)
            tags = tagsrex.findall(word)
            w = Word(lemma, tags)
            sentence.add_word(w)

        return sentence


class Tree(object):

    def __init__(self, root, subtrees=None):
        self.root = root
        if subtrees is None:
            self.subtrees = []
        else:
            self.subtrees = subtrees

    def __eq__(self, other):
        if not isinstance(other, Tree):
            return NotImplemented
        return type(self) == type(other) and \
               (self.root, self.subtrees) == (other.root, other.subtrees)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.root, tuple(self.subtrees)))

    def repr(self, leaf_fmt):
        if self.subtrees:
            subreprs = ", ".join(x.repr(leaf_fmt) for x in self.subtrees)
            return "%s{%s}" % (leaf_fmt(self.root), subreprs)
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
        return list(PreorderWalk(self))

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
        max_depth = 0
        while stack:
            depth, top = stack[0]
            max_depth = max(depth, max_depth)
            stack[:1] = [(depth + 1, x) for x in top.subtrees]
        return max_depth

    def split(self, separator=None):
        if separator is None: separator = self.root
        if self.root == separator:
            return [item for s in self.subtrees for item in s.split(separator)]
        else:
            return [self]

    def fold(self):
        return type(self)(self.root, self.split())


# @deprecated: clients should use adt.tree.walk.RichTreeWalk instead
# from PaladinEngine.tests.test_resources.lab1.lib.adt.tree.walk import PreorderWalk, RichTreeWalk as Walk
# Visitor = Walk.Visitor


class ParseTrees:
    def __init__(self, parser):
        """Initialize a syntax tree parsing process"""
        self.parser = parser
        self.charts = parser.charts
        self.length = len(parser)

        self.nodes = []
        for root in parser.complete_parses:
            self.nodes.extend(self.build_nodes(root))

    def __len__(self):
        """Trees count"""
        return len(self.nodes)

    def __repr__(self):
        """String representation of a list of trees with indexes"""
        return '<Parse Trees>\n{0}</Parse Trees>' \
            .format('\n'.join("Parse tree #{0}:\n{1}\n\n" \
                              .format(i + 1, str(self.nodes[i]))
                              for i in range(len(self))))

    def build_nodes(self, root):
        """Recursively create subtree for given parse chart row"""
        # find subtrees of current symbol
        if root.completing:
            down = self.build_nodes(root.completing)
        elif root.dot > 0:
            down = [Tree(root.prev_category())]
        else:
            down = []

        # prepend subtrees of previous symbols
        prev = root.previous
        left = []
        if prev:
            left[:0] = [x.subtrees for x in self.build_nodes(prev)]
            prev = prev.previous
        else:
            left = [[]]

        for x in left:
            x.extend(down)

        return [Tree(root.rule.lhs, subtrees) for subtrees in left]


class Parser:
    GAMMA_SYMBOL = 'γ'

    def __init__(self, grammar, sentence, debug=False):
        """Initialize parser with grammar and sentence"""
        self.grammar = grammar
        self.sentence = sentence if isinstance(sentence, Sentence) else Sentence(sentence)
        self.debug = debug

        # prepare a chart for every input word
        self.charts = [Chart([]) for _ in range(len(self) + 1)]
        self.complete_parses = []

    def __len__(self):
        """Length of input sentence"""
        return len(self.sentence)

    def init_first_chart(self):
        """Add initial Gamma rule to first chart"""
        row = ChartRow(Rule(Parser.GAMMA_SYMBOL, [self.grammar.start_symbol or 'S']), 0, 0)
        self.charts[0].add_row(row)

    def prescan(self, chart, position):
        """Scan current word in sentence, and add appropriate
           grammar categories to current chart"""
        word = self.sentence[position - 1]
        if word:
            rules = [Rule(tag, [word.word]) for tag in word.tags]
            for rule in rules:
                chart.add_row(ChartRow(rule, 1, position - 1))

    def predict(self, chart, position):
        """Predict next parse by looking up grammar rules
           for pending categories in current chart"""
        for row in chart.rows:
            next_cat = row.next_category()
            rules = self.grammar[next_cat]
            if rules:
                for rule in rules:
                    new = ChartRow(rule, 0, position)
                    chart.add_row(new)

    def complete(self, chart, position):
        """Complete a rule that was done parsing, and
           promote previously pending rules"""
        for row in chart.rows:
            if row.is_complete():
                completed = row.rule.lhs
                for r in self.charts[row.start].rows:
                    if completed == r.next_category():
                        new = ChartRow(r.rule, r.dot + 1, r.start, r, row)
                        chart.add_row(new)

    def parse(self):
        """Main Earley's Parser loop"""
        self.init_first_chart()

        i = 0
        # we go word by word
        while i < len(self.charts):
            chart = self.charts[i]
            self.prescan(chart, i)  # scan current input

            # predict & complete loop
            # rinse & repeat until chart stops changing
            length = len(chart)
            old_length = -1
            while old_length != length:
                self.predict(chart, i)
                self.complete(chart, i)

                old_length = length
                length = len(chart)

            i += 1

        # finally, print charts for debuggers
        if self.debug:
            print("Parsing charts:")
            for i in range(len(self.charts)):
                print("-----------{0}-------------".format(i))
                print(self.charts[i])
                print("-------------------------".format(i))

    def is_valid_sentence(self):
        """Returns true if sentence has a complete parse tree"""
        res = False
        for row in self.charts[-1].rows:
            if row.start == 0:
                if row.rule.lhs == self.GAMMA_SYMBOL:
                    if row.is_complete():
                        self.complete_parses.append(row)
                        res = True
        return res


class Rule:
    def __init__(self, lhs, rhs):
        """Initializes grammar rule: LHS -> [RHS]"""
        self.lhs = lhs
        self.rhs = rhs

    def __len__(self):
        """A rule's length is its RHS's length"""
        return len(self.rhs)

    def __repr__(self):
        """Nice string representation"""
        return "<Rule {0} -> {1}>".format(self.lhs, ' '.join(self.rhs))

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
        self.start_symbol = None

    def __repr__(self):
        """Nice string representation"""
        st = '<Grammar>\n'
        for group in self.rules.values():
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
        if lhs in self.rules:
            self.rules[lhs].append(rule)
        else:
            #self.rules[lhs] = [rule]
            d = self.rules
            d[lhs] = [rule]

        if self.start_symbol is None:
            self.start_symbol = lhs

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
        for line in iterable:
            # ignore comments
            comm = line.find('#')
            if comm >= 0:
                line = line[:comm]

            line = line.strip()
            if line == '':
                continue

            rule = line.split('->', 1)
            if len(rule) != 2:
                raise ValueError("invalid grammar format: '%s'" % line)
            lhs = rule[0].strip()
            for outcome in rule[1].split('|'):
                rhs = outcome.strip()
                symbols = rhs.split(' ') if rhs else []
                r = Rule(lhs, symbols)
                grammar.add_rule(r)

        return grammar


class SillyLexer(object):
    TEXT = 1
    TOKEN = 2

    def __init__(self, token_regexp):
        if not isinstance(token_regexp, str):
            if isinstance(token_regexp, Iterable):
                token_regexp = "|".join(token_regexp)
            else:
                raise ValueError("invalid token specification")
        self.token_re = re.compile(token_regexp)

    def __call__(self, input_text):
        for (a, val) in self.raw(input_text):
            if a == self.TOKEN:
                yield val

    def raw(self, input_text):
        pos = 0

        for mo in self.token_re.finditer(input_text):
            (from_, to) = mo.span()
            if from_ > pos:
                yield self.TEXT, input_text[from_:pos]
            yield self.TOKEN, self.mktoken(mo)
            pos = to

    def mktoken(self, mo):
        return Word(mo.group(), [mo.lastgroup or mo.group()])


class SillyBlocker(object):

    def __init__(self, open_token, close_token):
        self.topen = open_token
        self.tclose = close_token

    def __call__(self, token_stream):
        bal = 0
        topen, tclose = self.topen, self.tclose
        bag = []
        for t in token_stream:
            if t == topen:
                bal += 1
            elif t == tclose:
                bal -= 1
            bag += [t]
            if bal == 0:
                yield Tree(t, list(self(bag[1:-1])))
                bag = []

        if bal != 0:
            raise SyntaxError("unbalanced '%s' and '%s'" % (self.topen, self.tclose))


class LambdaParser(object):
    TOKENS = r"(let|in)(?![\w\d_])   (?P<id>[^\W\d]\w*)   (?P<num>\d+)   [\\.()=]".split()
    GRAMMAR = r"""
    E    ->  \. | let_    |   E1  |  E1'
    E1   ->  @            |   E0
    E1'  ->  @'           |   E0
    E0   ->  id | num     |  ( E )
    \.   ->  \ L . E 
    @    ->  E1 E0
    @'   ->  E1 \.
    L    ->  id L |
    let_ ->  let id = E in E
    """

    def __init__(self):
        self.tokenizer = SillyLexer(self.TOKENS)
        self.grammar = Grammar.from_string(self.GRAMMAR)

    def __call__(self, program_text: str) -> Optional[Tree]:
        tokens = list(self.tokenizer(program_text))

        earley = Parser(grammar=self.grammar, sentence=tokens, debug=False)
        earley.parse()

        if earley.is_valid_sentence():
            trees = ParseTrees(earley)
            assert (len(trees) == 1)
            return self.postprocess(trees.nodes[0])
        else:
            return None

    def postprocess(self, t: Tree) -> Tree:
        if t.root in ['γ', 'E', 'E0', 'E1', "E1'"] and len(t.subtrees) == 1:
            return self.postprocess(t.subtrees[0])
        elif t.root == 'E0' and t.subtrees[0].root == '(':
            return self.postprocess(t.subtrees[1])
        elif t.root == r'\.':
            args = t.subtrees[1].split()
            t = reduce(lambda t, a: Tree('\\', [a, t]), reversed(args), t.subtrees[3])
        elif t.root == "@'":
            t = Tree('@', t.subtrees)
        elif t.root == 'L':
            t = Tree('.', t.split())

        return Tree(t.root, [self.postprocess(s) for s in t.subtrees])


"""
Formats an expression for pretty printing.
Should be called as pretty(e), admitting the default values for `parent` and `follow`;
these values are suitable for the top-level term.
They are used subsequently by recursive calls.
"""


def pretty(expr: Tree, parent: Tuple[str, int] = ('.', 0), follow: str = '') -> str:
    if expr.root in ['id', 'num']:
        return expr.subtrees[0].root
    if expr.root == '\\':
        tmpl = r"\%s. %s"
        if parent == ('@', 0) or parent[0] == follow == '@':
            tmpl = "(%s)" % tmpl
    elif expr.root == '@':
        tmpl = "%s %s"
        if parent == ('@', 1):
            tmpl = "(%s)" % tmpl
    else:
        return str(expr)

    n = len(expr.subtrees)
    return tmpl % tuple(pretty(s, (expr.root, i), expr.root if i < n - 1 else follow)
                        for i, s in enumerate(expr.subtrees))


#
if __name__ == '__main__':
    parser = LambdaParser()
    #expr = LambdaParser()(r"\x. x \z g. y 6")
    expr = parser(r"\x. x \z g. y 6")
    parser = LambdaParser()
    expr2 = parser(r"\x. x \z g. y 6 5 4")
    if expr:
        print(">> Valid expression.")

        print(expr)
    #    dot_print(expr)
    else:
        print(">> Invalid expression.")
