import oracle
import parseitems
import terms
import unittest


class ItemsTestCase(unittest.TestCase):

    def test_example1(self):
        words = ('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population')
        actions = [
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
            ('idle',),
        ]
        target_mr = terms.from_string('answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
        self._test_action_sequence(words, actions, target_mr)

    def test_example2(self):
        words = ('could', 'you', 'tell', 'me', 'what', 'is', 'the', 'highest',
            'point', 'in', 'the', 'state', 'of', 'oregon', '?')
        actions = [
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('shift', 1, 'highest(A,B)'),
            ('coref', (1,), (1,)),
            ('drop', (2,)),
            ('shift', 1, 'place(A)'),
            ('coref', (2, 1,), (1,)),
            ('drop', (2, 2)),
            ('shift', 1, 'loc(A,B)'),
            ('coref', (2, 2, 1), (1,)),
            ('drop', (2, 2)),
            ('skip',),
            ('shift', 1, 'state(A)'),
            ('coref', (2, 2, 2), (1,)),
            ('drop', (2, 2)),
            ('skip',),
            ('shift', 1, 'const(A,stateid(oregon))'),
            ('coref', (2, 2, 1), (1,)),
            ('drop', (2, 2,)),
            ('skip',),
            ('finish',),
            ('idle',),
        ]
        target_mr = terms.from_string('answer(A,highest(A,(place(A),loc(A,B),state(B),const(B,stateid(oregon)))))')
        self._test_action_sequence(words, actions, target_mr)

    def test_example3(self):
        words = ('how', 'many', 'big', 'cities', 'are', 'in', 'pennsylvania', '?')
        actions = [
            ('skip',),
            ('shift', 1, 'count(A,B,C)'),
            ('coref', (1,), (3,)),
            ('drop', (2,)),
            ('shift', 1, 'major(A)'),
            ('coref', (2, 1), (1,)),
            ('drop', (2, 2)),
            ('shift', 1, 'city(A)'),
            ('coref', (2, 2, 1), (1,)),
            ('drop', (2, 2)),
            ('skip',),
            ('shift', 1, 'loc(A,B)'),
            ('coref', (2, 2, 1), (1,)),
            ('drop', (2, 2)),
            ('shift', 1, 'const(A,stateid(pennsylvania))'),
            ('coref', (2, 2, 2), (1,)),
            ('drop', (2, 2)),
            ('skip',),
            ('finish',),
            ('idle',),
        ]
        target_mr = terms.from_string('answer(A,count(B,(major(B),city(B),loc(B,C),const(C,stateid(pennsylvania))),A))')
        self._test_action_sequence(words, actions, target_mr)

    def test_example4(self):
        words = ('how', 'many', 'rivers', 'do', 'not', 'traverse', 'the', 'state', 'with', 'the', 'capital', 'albany', '?')
        target_mr = terms.from_string('answer(A,count(B,(river(B),\+ (traverse(B,C),state(C),loc(D,C),capital(D),const(D,cityid(albany,_)))),A))')
        actions = [
            ('skip',),
            ('shift', 1, 'count(A,B,C)'),
            ('coref', (1,), (3,)),
            ('drop', (2,)),
            ('shift', 1, 'river(A)'),
            ('coref', (2, 1), (1,)),
            ('drop', (2, 2)),
            ('skip',),
            ('shift', 1, '\+A'),
            ('drop', (2, 2)),
            ('shift', 1, 'traverse(A,B)'),
            ('coref', (2, 1), (1,)),
            ('drop', (2, 2, 1)),
            ('skip',),
            ('shift', 1, 'state(A)'),
            ('coref', (2, 2, 1, 2), (1,)),
            ('drop', (2, 2, 1)),
            ('shift', 1, 'loc(A,B)'),
            ('coref', (2, 2, 1, 1), (2,)),
            ('drop', (2, 2, 1)),
            ('skip',),
            ('shift', 1, 'capital(A)'),
            ('coref', (2, 2, 1, 1), (1,)),
            ('drop', (2, 2, 1)),
            ('shift', 1, 'const(A,cityid(albany,B))'),
            ('coref', (2, 2, 1, 1), (1,)),
            ('drop', (2, 2, 1)),
            ('skip',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

    def _test_action_sequence(self, words, actions, target_mr):
        """Tests that the given action sequence is found.

        Tests that given the words and target_mr, the given actions are found
        and allowed by the oracle.
        """
        item = parseitems.initial(words)
        rejector = oracle.Rejector(target_mr)
        for action in actions:
            item.successor(action)
            successors = item.successors()
            successors = [s for s in successors if s.action == action]
            self.assertTrue(successors, '{} not applied to {}'.format(action, item))
            self.assertEqual(len(successors), 1)
            item = successors[0]
            self.assertFalse(rejector.reject(item), '{} rejected'.format(item))
        self.assertTrue(item.finished)
