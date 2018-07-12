import lexicon
import re
import terms


UNAUGMENT_PATTERN = re.compile(r'_\d+$')


class AugmentingLexicon:

    def __init__(self, lex, target_mr):
        self.lex = lex
        mr = target_mr.augment()
        self.lst = list(lexicon.lexical_subterms(mr))
        for l in self.lst:
            print(l.to_string())
        self.lst = [terms.from_string(l.to_string()) for l in self.lst] # undo variable bindings

    def meanings(self, word):
        meanings = self.lex.meanings(word)
        for m in meanings:
            for l in self.lst:
                unaugmented = terms.ComplexTerm(unaugment(l.functor_name), l.args)
                if unaugmented.equivalent(m):
                    yield l


def unaugment(name):
    return UNAUGMENT_PATTERN.sub('', name)
