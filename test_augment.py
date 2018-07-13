import augment
import terms
import lexicon
import unittest


class AugmentTestCase(unittest.TestCase):

    def test_augment1(self):
        lex = lexicon.read_lexicon('lexicon.txt')
        t = terms.from_string('answer(A,longest(A,(river(A),traverse(A,B),state(B),next_to(B,C),most(C,D,(state(C),next_to(C,D),state(D))))))')
        alex = augment.AugmentingLexicon(lex, t)
        word = ('longest',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['longest_1(A,B)'])
        word = ('river',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['river_1(A)'])
        word = ('passes',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['traverse_1(A,B)'])
        word = ('states',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['state_1(A)', 'state_2(A)', 'state_3(A)'])
        word = ('border',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['next_to_1(A,B)', 'next_to_2(A,B)'])
        word = ('state',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['state_1(A)', 'state_2(A)', 'state_3(A)'])
        word = ('borders',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['next_to_1(A,B)', 'next_to_2(A,B)'])
        word = ('most',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['most_1(A,B,C)'])

    def test_augment2(self):
        lex = lexicon.read_lexicon('lexicon.txt')
        t = terms.from_string('answer(A,lowest(B,(state(A),traverse(C,A),const(C,riverid(mississippi)),loc(B,A),place(B))))')
        alex = augment.AugmentingLexicon(lex, t)
        word = ('states',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['state_1(A)'])
        word = ('washed',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['traverse_1(A,B)'])
        word = ('mississippi',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['const_1(A,riverid(mississippi))'])
        word = ('has',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['loc_1(A,B)'])
        word = ('lowest',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['lowest_1(A,B)'])
        word = ('point',)
        meanings = [m.to_string() for m in alex.meanings(word)]
        self.assertEqual(meanings, ['place_1(A)'])
