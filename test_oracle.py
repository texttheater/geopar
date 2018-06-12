import data
import oracle
import parseitems
import terms
import unittest


class OracleTest(unittest.TestCase):

    def test_example1(self):
        words = ('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population')
        target_mr = terms.from_string('answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
        actions_gold = [
                ('skip',),
                ('skip',),
                ('skip',),
                ('shift', 1, 'capital(A,B)'),
                ('coref', (1,), (2,)),
                ('drop', (2,)),
                ('skip',),
                ('skip',),
                ('shift', 1, 'state(A)'),
                ('coref', (2, 1), (1,)),
                ('skip',),
                ('skip',),
                ('shift', 1, 'largest(A,B)'),
                ('lift', (2,)),
                ('drop', (2,)),
                ('shift', 1, 'population(A,B)'),
                ('coref', (2, 2, 1), (1,)),
                ('coref', (2, 1,), (2,)),
                ('drop', (2, 2)),
                ('finish',),
        ]
        actions_oracle = oracle.action_sequence(words, target_mr)
        self.assertEqual(actions_gold, actions_oracle)

    def test_coverage(self):
        """Tests that an action sequence is found for every training example.
        """
        for words, mr in data.geo880_train():
            print(' '.join(words))
            print(mr.to_string())
            item = oracle.action_sequence(words, mr)
