import collections
import lexicon
import re
import terms


UNAUGMENT_PATTERN = re.compile(r'\d+$')


class AugmentingLexicon:

    def __init__(self, lex, target_mr):
        self.lex = lex
        mr = target_mr.augment(collections.Counter())
        self.lst = list(lexicon.lexical_subterms(mr))

    def meanings(self, word):
        meanings = self.lex.meanings(word)
        for m in meanings:
            for l in self.lst:
                unaugmented = terms.ComplexTerm(UNAUGMENT_PATTERN.sub('', l.functor_name), l.args)
                if unaugmented.equivalent(m):
                    yield l

