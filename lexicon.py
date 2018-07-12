import collections
import os
import terms


def read_lexicon(path):
    word_term_map = collections.defaultdict(list)
    with open(path) as f:
        for line in f:
            if not line.split() or line.startswith('#'):
                continue
            mr, word = line.rsplit(maxsplit=1)
            tokens = tuple(word.split(','))
            word_term_map[tokens].append(mr)
    return Lexicon(word_term_map)


class Lexicon:

    def __init__(self, word_term_map):
        self.word_term_map = word_term_map

    def meanings(self, word):
        """Returns the known meanings of a word.
        """
        if word in self.word_term_map:
            return (terms.from_string(s) for s in self.word_term_map[word])
        return ()


def lexical_subterms(term):
    """Breaks a term up into "lexical" factors.

    We consider the lexical factors of a GeoQuery MR to be 1) const/2 terms,
    and 2) all other complex terms, but with all-variable arguments.
    """
    if isinstance(term, terms.ComplexTerm):
        if term.functor_name == 'const' and len(term.args) == 2:
            yield term
        else:
            args = []
            for arg in term.args:
                if isinstance(arg, terms.ComplexTerm) \
                    or isinstance(arg, terms.ConjunctiveTerm):
                    yield from lexical_subterms(arg)
                    args.append(terms.Variable())
                else:
                    args.append(arg)
            yield terms.ComplexTerm(term.functor_name, args)
    elif isinstance(term, terms.ConjunctiveTerm):
        for conjunct in term.conjuncts:
            yield from lexical_subterms(conjunct)
    else:
        return
