import data
import lexicon
import oracle
import parseitems
import terms
import unittest


class OracleTest(unittest.TestCase):

    #def test_example1(self):
    #    words = ('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population')
    #    target_mr = terms.from_string('answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
    #    actions_gold = [
    #        ('skip',),
    #        ('skip',),
    #        ('skip',),
    #        ('shift', 1, 'capital_1(A,B)'),
    #        ('coref', 0, 1, 0, 2),
    #        ('drop', 2),
    #        ('skip',),
    #        ('skip',),
    #        ('shift', 1, 'state_1(A)'),
    #        ('coref', 0, 1, 0, 1),
    #        ('skip',),
    #        ('skip',),
    #        ('shift', 1, 'largest_1(A,B)'),
    #        ('lift', 2),
    #        ('shift', 1, 'population_1(A,B)'),
    #        ('coref', 0, 1, 0, 1),
    #        ('coref', 1, 1, 0, 2),
    #        ('sdrop',),
    #        ('pop',),
    #        ('pop',),
    #        ('sdrop',),
    #        ('pop',),
    #        ('pop',),
    #        ('finish',),
    #    ]
    #    actions_oracle = oracle.action_sequence(words, target_mr)
    #    self.assertEqual(actions_gold, actions_oracle)

    #def test_example2(self):
    #    words = ('how', 'many', 'rivers', 'do', 'not', 'traverse', 'the', 'state', 'with', 'the', 'capital', 'albany', '?')
    #    target_mr = terms.from_string('answer(A,count(B,(river(B),\+ (traverse(B,C),state(C),loc(D,C),capital(D),const(D,cityid(albany,_)))),A))')
    #    oracle.action_sequence(words, target_mr)

    #def test_coverage(self):
    #    """Tests that an action sequence is found for every training example.
    #    """
    #    for words, mr in data.geo880_train():
    #        print(' '.join(words))
    #        print(mr.to_string())
    #        item = oracle.action_sequence(words, mr)
    #        print()

    def test_coverage(self):
        for words, target_mr in data.geo880_train():
            print(' '.join(words))
            print(target_mr.to_string())
            actions = oracle.action_sequence(words, target_mr)
            item = parseitems.initial(words, terms.from_string('root(_)'), terms.from_string('answer(_,_)'))
            lex = lexicon.read_lexicon('lexicon.txt')
            for action in actions:
                item = item.successor(action, lex)
            self.assertTrue(item.finished)
            self.assertIsNotNone(item.root)
            self.assertTrue(item.root.unaugment().args[0].equivalent(target_mr))
