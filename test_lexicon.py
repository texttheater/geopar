"""This program checks the coverage of GeoPar's lexicon.

For each NLU-MR pair in the training data, for each lexical term in the MR, it
checks whether there is a word or multiword (up to length 2) in the NLU that in
the lexicon is associated with that lexical term. Prints a warning if not.
"""


import data
import lexicon
import terms
import itertools
import unittest
import util


class LexiconCoverageTestCase(unittest.TestCase):

    def test(self):
        """Tests the coverage of GeoPar's lexicon.

        For each MLU-NR pair in the training data, for each lexical term in the
        MR, it checks whether there is a word or multiword (up to length 3) in
        the NLU that in the lexicon is associated with that lexical term.
        """
        missing_terms = []
        lex = lexicon.read_lexicon('lexicon.txt')
        for words, mr in data.geo880_train():
            printed = False
            self.assertEqual(mr.functor_name, 'answer')
            self.assertEqual(len(mr.args), 2)
            self.assertIsInstance(mr.args[0], terms. Variable)
            for lexterm in lexicon.lexical_subterms(mr.args[1]):
                word_found = False
                unigrams = util.ngrams(1, words)
                bigrams = util.ngrams(2, words)
                trigrams = util.ngrams(3, words)
                for word in itertools.chain(unigrams, bigrams, trigrams):
                    for term in lex.meanings(word):
                        if term.equivalent(lexterm):
                            word_found = True
                            break
                if not word_found:
                    if not printed:
                        print(str(words))
                        printed = True
                    print('WARNING: no word found that means ' + lexterm.to_string())
                    missing_terms.append(lexterm)
        self.assertEqual(missing_terms, [])
