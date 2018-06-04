"""Classes and methods for representing GeoQuery terms.

There are different term classes for different kinds of terms: Variable, Atom,
Number, ComplexTerm, ConjunctiveTerm. List is also a term class but has
limited functionality because GeoQuery MRs do not contain lists, lists are only
used to represent token lists in NLU-MR pairs.

Reading and Writing Terms
=========================

Strings like 'capital(S, C)' can be converted into a term object either
directly with the from_string function or by creating TermReader object and
using its read_term method. The TermReader object can subsequently be passed to
the to_string method of the term or its subterms, which has the advantage that
variables retain their original names when converting back to strings.

Term Addresses
==============

A subterm S in a complex term T has an address. An address is a list of pairs
of integers. The first component of each pair represents an argument number,
the second, the position of a conjunct inside a conjunctive term (or 1 if the
term isn't conjunctive). For example:

    S        T                               ADDRESS
    a(A, B)  b(C, a(A, B))                   [(2, 1)]
    a(A, B)  b(C, (a(A, B), c(D, E)))        [(2, 1)]
    c(D, E)  b(C, (a(A, B), c(D, E)))        [(2, 2)]
    d(F, G)  b(C, (a(A, d(F, G)), c(D, E)))  [(2, 1), (2, 1)]

Addresses are useful for "integrating" a new term U into T at some specific
address, as is done in the "drop" and "lift" parse actions. For details, see
the ComplexTerm.integrate method.

Replacing Terms
===============

All term classes (except List) implement the replace method.
term.replace(old, new) where old and new are terms returns a new version of
term where all token-identical occurrences of old have been replaced with new.
Note that equivalence implies token-identity only for variables.
"""

import re


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


class Variable:

    def to_string(self, term_reader=None):
        if term_reader is None:
            term_reader = TermReader()
        for name, var in term_reader.name_variable_dict.items():
            if var == self:
                return name
        return '_'

    def lexterms(self):
        return
        yield

    def subterms(self):
        yield self

    def equivalent(self, other, alignments=None):
        if alignments is None:
            alignments = []
        if not isinstance(other, Variable):
            return False
        for a, b in alignments:
            if a == self:
                return b == other
            if b == other:
                return False
        alignments.append((self, other))
        return True

    def replace(self, old, new):
        if self == old:
            return new
        return self


class Atom:

    def __init__(self, name):
        self.name = name

    def to_string(self, term_reader=None):
        match = _ATOM_PATTERN.fullmatch(self.name)
        if match:
            return self.name
        return "'" + self.name.replace("\\", "\\\\").replace("'", "\\'") + "'"

    def lexterms(self):
        return
        yield

    def subterms(self):
        yield self

    def equivalent(self, other, alignments=None):
        return isinstance(other, Atom) and self.name == other.name

    def __str__(self):
        return self.name

    def replace(old, new):
        if self == old:
            return new
        return self


class ComplexTerm:

    def __init__(self, functor_name, args):
        self.functor_name = functor_name
        self.args = tuple(args)

    def to_string(self, term_reader=None):
        if term_reader is None:
            term_reader = TermReader()
        if self.functor_name == 'parse' and len(self.args) == 2:
            sep = ', ' # quirk in the data
        elif self.functor_name == '\\+' and len(self.args) == 1:
            if isinstance(self.args[0], ConjunctiveTerm):
                return '\\+ ' + self.args[0].to_string(term_reader)
            else:
                return '\\+' + self.args[0].to_string(term_reader)
        else:
            sep = ','
        return self.functor_name + '(' + sep.join(arg.to_string(term_reader) for arg in self.args) + ')'

    def lexterms(self):
        if self.functor_name == 'const' and len(self.args) == 2:
            yield self
        else:
            args = []
            for arg in self.args:
                if isinstance(arg, ComplexTerm) or isinstance(arg, ConjunctiveTerm):
                    yield from arg.lexterms()
                    args.append(Variable())
                else:
                    args.append(arg)
            yield ComplexTerm(self.functor_name, args)

    def subterms(self):
        yield self
        for arg in self.args:
            yield from arg.subterms()

    def equivalent(self, other, alignments=None):
        if not isinstance(other, ComplexTerm):
            return False
        if self.functor_name != other.functor_name:
            return False
        if len(self.args) != len(other.args):
            return False
        if alignments is None:
            alignments = []
        for a, b in zip(self.args, other.args):
            if not a.equivalent(b, alignments):
                return False
        return True

    def replace(self, old, new):
        if self == old:
            return new
        args_new = [arg.replace(old, new) for arg in self.args]
        return ComplexTerm(self.functor_name, args_new)

    def arg(self, address, i):
        """Returns the i-th argument of the subterm at the given address.
        """
        if address == []:
            return self.args[i - 1]
        else:
            arg_num, conj_num = address[0]
            address_tail = address[1:]
            arg = self.args[arg_num - 1]
            if isinstance(arg, ConjunctiveTerm):
                conj = arg.conjuncts[conj_num - 1]
            else:
                assert conj_num == 1
                conj = arg
            return conj.arg(address_tail, i)


class ConjunctiveTerm:

    def __init__(self, conjuncts):
        self.conjuncts = tuple(conjuncts)

    def to_string(self, term_reader=None):
        if term_reader is None:
            term_reader = TermReader()
        return '(' + ','.join(conjunct.to_string(term_reader) for conjunct in self.conjuncts) + ')'

    def lexterms(self):
        for conjunct in self.conjuncts:
            yield from conjunct.lexterms()

    def subterms(self):
        yield self
        for conjunct in self.conjuncts:
            yield from conjunct.subterms()

    def equivalent(self, other, alignments=None):
        if not isinstance(other, ConjunctiveTerm):
            return False
        if len(self.conjuncts) != len(other.conjuncts):
            return False
        if alignments is None:
            alignments = []
        for a, b in zip(self.conjuncts, other.conjuncts):
            if not a.equivalent(b, alignments):
                return False
        return True

    def replace(self, old, new):
        if self == old:
            return new
        conjuncts_new = [conj.replace(old, new) for conj in self.conjuncts]
        return ConjunctiveTerm(conjuncts_new)


class Number:

    def __init__(self, number):
        self.number = number

    def to_string(self, term_reader=None):
        return str(self.number)

    def lexterms(self):
        yield self

    def subterms(self):
        yield self

    def equivalent(self, other, alignments=None):
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

    def to_string(self, term_reader=None):
        if term_reader is None:
            term_reader = TermReader()
        return '[' + ','.join(element.to_string(term_reader) for element in self.elements) + ']'


class TermReader:

    def __init__(self):
        self.name_variable_dict = {}

    def variable(self, name=None):
        if name is None:
            return Variable()
        if not name in self.name_variable_dict:
            var = Variable()
            self.name_variable_dict[name] = var
        return self.name_variable_dict[name]

    def atom(self, name):
        return Atom(name)

    def number(self, number):
        return Number(number)

    def read_term(self, string):
        match = _VARIABLE_PATTERN.match(string)
        if match:
            variable_name = match.group()
            rest = string[match.end():]
            return self.variable(variable_name), rest
        match = _ANONYMOUS_VARIABLE_PATTERN.match(string)
        if match:
            rest = string[match.end():]
            return self.variable(), rest
        match = _COMPLEX_TERM_START_PATTERN.match(string)
        if match:
            functor_name = match.group('functor_name')
            rest = string[match.end():]
            args = []
            arg1, rest = self.read_term(rest)
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
                arg, rest = self.read_term(rest)
                args.append(arg)
        match = _ATOM_PATTERN.match(string)
        if match:
            name = match.group()
            rest = string[match.end():]
            return self.atom(name), rest
        match = _QUOTED_ATOM_PATTERN.match(string)
        if match:
            name = _unquote(match.group())
            rest = string[match.end():]
            return self.atom(name), rest
        match = _NUMBER_PATTERN.match(string)
        if match:
            number = int(match.group())
            rest = string[match.end():]
            return self.number(number), rest
        match = _LIST_START_PATTERN.match(string)
        if match:
            rest = string[match.end():]
            elements = []
            element1, rest = self.read_term(rest)
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
                element, rest = self.read_term(rest)
                elements.append(element)
        match = _CONJUNCTIVE_TERM_START_PATTERN.match(string)
        if match:
            rest = string[match.end():]
            conjuncts = []
            conjunct1, rest = self.read_term(rest)
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
                conjunct, rest = self.read_term(rest)
                conjuncts.append(conjunct)
        match = _NEGATION_START_PATTERN.match(string)
        if match:
            rest = string[match.end():]
            scope, rest = self.read_term(rest)
            return ComplexTerm('\\+', [scope]), rest
        raise RuntimeError("couldn't parse term suffix: " + string)


def from_string(string):
    reader = TermReader()
    term, _ = reader.read_term(string)
    return term
