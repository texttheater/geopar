"""Classes and methods for representing GeoQuery terms.

There are different term classes for different kinds of terms: Variable, Atom,
Number, ComplexTerm, ConjunctiveTerm. List is also a term class but has
limited functionality because GeoQuery MRs do not contain lists, lists are only
used to represent token lists in NLU-MR pairs.

Reading and Writing Terms
=========================

Strings like 'capital(S, C)' can be converted into a term object with the
from_string function. They can be serialized as strings (with canonicalized
variable names) with the to_string method.

Term Addresses
==============

The methods left_address and right_address, given a list of argument numbers to
be read from outermost to innermost, return the subterm at the given address.
Conjunctive terms cannot be addressed; the leftmost/rightmost conjunct is
addressed instead.

Replacing Terms
===============

All term classes (except List) implement the replace method.
term.replace(old, new) where old and new are terms returns a new version of
term where all token-identical occurrences of old have been replaced with new.
Note that equivalence implies token-identity only for variables.
"""


import collections
import re
import util


_VARIABLE_PATTERN = re.compile('[A-Z]')
_ANONYMOUS_VARIABLE_PATTERN = re.compile('_')
_COMPLEX_TERM_START_PATTERN = re.compile('(?P<functor_name>[a-z][a-z_]*)\(')
_COMMA_PATTERN = re.compile(', ?')
_COMPLEX_TERM_END_PATTERN = re.compile('\)')
_ATOM_PATTERN = re.compile('[a-z?]+')
_QUOTED_ATOM_PATTERN = re.compile('\'[a-z?. ]+\'')
_NUMBER_PATTERN = re.compile('[0-9]+')
_LIST_START_PATTERN = re.compile('\[')
_LIST_END_PATTERN = re.compile(']')
_CONJUNCTIVE_TERM_START_PATTERN = re.compile('\(')
_CONJUNCTIVE_TERM_END_PATTERN = re.compile('\)')
_NEGATION_START_PATTERN = re.compile(r'\\\+ ?')


def _unquote(quoted_atom):
    assert quoted_atom.startswith('\'')
    assert quoted_atom.endswith('\'')
    between_part = quoted_atom[1:-1]
    assert '\\' not in between_part
    assert '\'' not in between_part
    return between_part


class AddressError(Exception):

    """Signals that no subterm exists at the specified address.
    """

    pass


class Term:

    def equivalent(self, other):
        return self.subsumes(other) and other.subsumes(self)

    def subsumes_without_identification(self, other):
        """Check for subsumption without identifying variables within self.
        """
        bindings = {}
        if not self.subsumes(other, bindings):
            return False
        # check that no subterm is bound to twice:
        return len(bindings) == len(set(bindings.values()))

    def left_address(self, address):
        if not len(address) == 0:
            raise AddressError()
        return self

    def right_address(self, address):
        if not len(address) == 0:
            raise AddressError()
        return self


class Variable(Term):

    def to_string(self, var_name_dict=None):
        if var_name_dict is None:
            var_name_dict = make_var_name_dict()
        return var_name_dict[self]

    def subterms(self):
        yield self

    def fragments(self):
        yield self

    def subsumes(self, other, bindings=None):
        if bindings is None:
            bindings = {}
        if self in bindings:
            return other == bindings[self]
        bindings[self] = other
        return True

    def replace(self, old, new):
        if self == old:
            return new
        return self


class Atom(Term):

    def __init__(self, name):
        self.name = name

    def to_string(self, var_name_dict=None):
        match = _ATOM_PATTERN.fullmatch(self.name)
        if match:
            return self.name
        return "'" + self.name.replace("\\", "\\\\").replace("'", "\\'") + "'"

    def subterms(self):
        yield self

    def fragments(self):
        yield self

    def subsumes(self, other, bindings=None):
        if not isinstance(other, Atom):
            return False
        if not other.name == self.name:
            return False
        return True

    def __str__(self):
        return self.name

    def replace(self, old, new):
        if self == old:
            return new
        return self


class ComplexTerm(Term):

    def __init__(self, functor_name, args):
        self.functor_name = functor_name
        self.args = tuple(args)

    def to_string(self, var_name_dict=None):
        if var_name_dict is None:
            var_name_dict = make_var_name_dict()
        if self.functor_name == 'parse' and len(self.args) == 2:
            sep = ', ' # quirk in the data
        elif self.functor_name == '\\+' and len(self.args) == 1:
            if isinstance(self.args[0], ConjunctiveTerm):
                return '\\+ ' + self.args[0].to_string(var_name_dict)
            else:
                return '\\+' + self.args[0].to_string(var_name_dict)
        else:
            sep = ','
        return self.functor_name + '(' + sep.join(arg.to_string(var_name_dict) for arg in self.args) + ')'

    def subterms(self):
        yield self
        for arg in self.args:
            yield from arg.subterms()

    def fragments(self):
        for arg in self.args:
            yield from arg.fragments()
        for args_fragments in fragments(self.args):
            yield ComplexTerm(self.functor_name, args_fragments)

    def subsumes(self, other, bindings=None):
        if not isinstance(other, ComplexTerm):
            return False
        if other.functor_name != self.functor_name:
            return False
        if len(other.args) != len(self.args):
            return False
        if bindings is None:
            bindings = {}
        for a, b in zip(self.args, other.args):
            if not a.subsumes(b, bindings):
                return False
        return True

    def replace(self, old, new):
        if self == old:
            return new
        args_new = [arg.replace(old, new) for arg in self.args]
        return ComplexTerm(self.functor_name, args_new)

    def left_address(self, address):
        if len(address) == 0:
            return self
        return self.args[address[0] - 1].left_address(address[1:])

    def right_address(self, address):
        if len(address) == 0:
            return self
        return self.args[address[0] - 1].right_address(address[1:])


class ConjunctiveTerm(Term):

    def __init__(self, conjuncts):
        self.conjuncts = tuple(conjuncts)

    def to_string(self, var_name_dict=None):
        if var_name_dict is None:
            var_name_dict = make_var_name_dict()
        return '(' + ','.join(conjunct.to_string(var_name_dict) for conjunct in self.conjuncts) + ')'

    def subterms(self):
        yield self
        for conjunct in self.conjuncts:
            yield from conjunct.subterms()

    def fragments(self):
        for conj in self.conjuncts:
            yield from conj.fragments()
        for length in range(2, len(self.conjuncts) + 1):
            for conjuncts_fragments in fragments(self.conjuncts[:length]):
                yield ConjunctiveTerm(conjuncts_fragments)
        for start in range(1, len(self.conjuncts) - 1):
            for conjuncts_fragments in fragments(self.conjuncts[start:]):
                yield ConjunctiveTerm(conjuncts_fragments)

    def subsumes(self, other, bindings=None):
        if not isinstance(other, ConjunctiveTerm):
            return False
        if len(other.conjuncts) != len(self.conjuncts):
            return False
        if bindings is None:
            bindings = {}
        for a, b in zip(self.conjuncts, other.conjuncts):
            if not a.subsumes(b, bindings):
                return False
        return True

    def replace(self, old, new):
        if self == old:
            return new
        conjuncts_new = [conj.replace(old, new) for conj in self.conjuncts]
        return ConjunctiveTerm(conjuncts_new)

    def left_address(self, address):
        return self.conjuncts[0].left_address(address)

    def right_address(self, address):
        return self.conjuncts[-1].right_address(address)


class Number(Term):

    def __init__(self, number):
        self.number = number

    def to_string(self, var_name_dict=None):
        return str(self.number)

    def subterms(self):
        yield self

    def fragments(self):
        yield self

    def subsumes(self, other, bindings=None):
        if not isinstance(other, Number):
            return False
        return self.number == other.number

    def __str__(self):
        return str(self.number)

    def replace(self, old, new):
        if self == old:
            return new
        return self


class List:

    def __init__(self, elements):
        self.elements = elements

    def to_string(self, var_name_dict=None):
        if var_name_dict is None:
            var_name_dict = make_var_name_dict()
        return '[' + ','.join(element.to_string(var_name_dict) for element in self.elements) + ']'


def read_term(string, name_var_dict=None):
    if name_var_dict is None:
        name_var_dict = collections.defaultdict(Variable)
    match = _VARIABLE_PATTERN.match(string)
    if match:
        variable_name = match.group()
        rest = string[match.end():]
        return name_var_dict[variable_name], rest
    match = _ANONYMOUS_VARIABLE_PATTERN.match(string)
    if match:
        rest = string[match.end():]
        return Variable(), rest
    match = _COMPLEX_TERM_START_PATTERN.match(string)
    if match:
        functor_name = match.group('functor_name')
        rest = string[match.end():]
        args = []
        arg1, rest = read_term(rest, name_var_dict)
        args.append(arg1)
        while True:
            match = _COMPLEX_TERM_END_PATTERN.match(rest)
            if match:
                rest = rest[match.end():]
                return ComplexTerm(functor_name, args), rest
            match = _COMMA_PATTERN.match(rest)
            if not match:
                raise RuntimeError("couldn't parse term suffix: " + rest)
            rest = rest[match.end():]
            arg, rest = read_term(rest, name_var_dict)
            args.append(arg)
    match = _ATOM_PATTERN.match(string)
    if match:
        name = match.group()
        rest = string[match.end():]
        return Atom(name), rest
    match = _QUOTED_ATOM_PATTERN.match(string)
    if match:
        name = _unquote(match.group())
        rest = string[match.end():]
        return Atom(name), rest
    match = _NUMBER_PATTERN.match(string)
    if match:
        number = int(match.group())
        rest = string[match.end():]
        return Number(number), rest
    match = _LIST_START_PATTERN.match(string)
    if match:
        rest = string[match.end():]
        elements = []
        element1, rest = read_term(rest, name_var_dict)
        elements.append(element1)
        while True:
            match = _LIST_END_PATTERN.match(rest)
            if match:
                rest = rest[match.end():]
                return List(elements), rest
            match = _COMMA_PATTERN.match(rest)
            if not match:
                raise RuntimeError("couldn't parse term suffix: " + rest)
            rest = rest[match.end():]
            element, rest = read_term(rest, name_var_dict)
            elements.append(element)
    match = _CONJUNCTIVE_TERM_START_PATTERN.match(string)
    if match:
        rest = string[match.end():]
        conjuncts = []
        conjunct1, rest = read_term(rest, name_var_dict)
        conjuncts.append(conjunct1)
        while True:
            match = _CONJUNCTIVE_TERM_END_PATTERN.match(rest)
            if match:
                rest = rest[match.end():]
                return ConjunctiveTerm(conjuncts), rest
            match = _COMMA_PATTERN.match(rest)
            if not match:
                raise RuntimeError("couldn't parse term suffix: " + rest)
            rest = rest[match.end():]
            conjunct, rest = read_term(rest, name_var_dict)
            conjuncts.append(conjunct)
    match = _NEGATION_START_PATTERN.match(string)
    if match:
        rest = string[match.end():]
        scope, rest = read_term(rest, name_var_dict)
        return ComplexTerm('\\+', [scope]), rest
    raise RuntimeError("couldn't parse term suffix: " + string)


def from_string(string):
    term, _ = read_term(string)
    return term


def variable_names():
    # The first 26 variable names are the letters of the alphabet:
    yield from 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # Then repeat ad infinitum, adding the number of the current iteration:
    for i in itertools.count(start=1):
        for l in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            yield l + str(i)
        

def make_var_name_dict():
    names = variable_names()
    return collections.defaultdict(lambda: next(names))


def fragments(args):
    if args == ():
        yield ()
    else:
        for f in args[0].fragments():
            for g in fragments(args[1:]):
                yield (f,) + g

