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
                ('shift', 1, 'population(A,B)'),
                ('coref', (2, 1), (1,)),
                ('coref', (1,), (2,)),
                ('drop', (2,)),
                ('drop', (2,)),
                ('finish',),
        ]
        item = oracle.first_finished_item(words, target_mr)
        actions_oracle = item.action_sequence()
        items_oracle = item.item_sequence()
        for i in items_oracle:
            print(i)
        self.assertEqual(actions_gold, actions_oracle)

    def test_coverage(self):
        """Tests that an action sequence is found for every training example.
        """
        for words, mr in data.geo880_train():
            print(' '.join(words))
            print(mr.to_string())
            item = oracle.first_finished_item(words, mr)

    def test_example2(self):
        words = ('give', 'me', 'the', 'cities', 'in', 'virginia')
        target_mr = terms.from_string('answer(A,(city(A),loc(A,B),const(B,stateid(virginia))))')
        item = parseitems.initial(words)
        self.assertTrue(oracle.accept(item, target_mr))
        item = item.skip()
        self.assertTrue(oracle.accept(item, target_mr))
        item = item.skip()
        self.assertTrue(oracle.accept(item, target_mr))
        item = item.skip()
        self.assertTrue(oracle.accept(item, target_mr))
        item = item.shift(1, terms.from_string('city(A)'))
        self.assertTrue(oracle.accept(item, target_mr))
        item = item.shift(1, terms.from_string('loc(A,B)'))
        self.assertTrue(oracle.accept(item, target_mr)) # should maybe not but ok
        item = item.coref((1,), (2,))
        self.assertFalse(oracle.accept(item, target_mr))
