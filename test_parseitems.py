import oracle
import parseitems
import terms
import unittest


class ItemsTestCase(unittest.TestCase):

    def test_example1(self):
        """Tests the successor(s) methods.

        Same as above, but this time we generate all items using the successors
        method and make sure that it generates all the correction actions/items.
        """
        item = parseitems.initial(('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population'))
        target_mr = terms.from_string('answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
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
            ('idle',)
        ]
        for action in actions:
            successors = item.successors()
            action_successor_dict = {s.action: s for s in successors}
            item = action_successor_dict[action]
            self.assertTrue(oracle.accept(item, target_mr))
        self.assertEqual(len(item.stack), 1)
        self.assertTrue(item.queue.is_empty())
        self.assertTrue(item.finished)
        self.assertTrue(item.stack.head.equivalent(target_mr))

    def test_example2(self):
        item = parseitems.initial(('could', 'you', 'tell', 'me', 'what', 'is', 'the', 'highest', 'point', 'in', 'the', 'state', 'of', 'oregon', '?'))
        target_mr = terms.from_string('answer(A,highest(A,(place(A),loc(A,B),state(B),const(B,stateid(oregon)))))')
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
        for action in actions:
            successors = item.successors()
            action_successor_dict = {s.action: s for s in successors}
            item = action_successor_dict[action]
            print(item)
            self.assertTrue(oracle.accept(item, target_mr))
        self.assertEqual(len(item.stack), 1)
        self.assertTrue(item.queue.is_empty())
        self.assertTrue(item.finished)
        self.assertTrue(item.stack.head.equivalent(target_mr))
