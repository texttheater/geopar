import parseitems
import terms
import unittest


class ItemsTestCase(unittest.TestCase):

    def test_items_example1_skip_shift(self):
        """Tests the implementation of the parsing actions.

        This test starts with the initial item for the example from the lecture
        notes (Table 1), applies the first four parsing actions from that
        example and succeeds if the correct item results."""
        item = parseitems.initial(('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population'))
        item = item.skip()
        item = item.skip()
        item = item.skip()
        item = item.shift(1, terms.from_string('capital(_, _)'))
        self.assertEqual(len(item.stack), 1)
        self.assertEqual(list(item.queue), ['of' 'the', 'state', 'with', 'the', 'largest', 'population'])
        self.assertTrue(item.stack.head.term.equivalent(terms.from_string('capital(_, _)')))

    def test_items_example1_full(self):
        """Tests the implementation of the parsing actions.

        This test starts with the initial item for the example from the lecture
        notes (Table 1), applies the parsing actions from that example and
        succeeds if the correct item results."""
        item = parseitems.initial(('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population'))
        item = item.skip()
        item = item.skip()
        item = item.skip()
        item = item.shift(1, terms.from_string('capital(_, _)'))
        item = item.coref(0, 1, 0, 2)
        item = item.drop(0, 2)
        item = item.skip()
        item = item.skip()
        item = item.shift(1, terms.from_string('state(_)'))
        item = item.coref(1, 1, 0, 1)
        item = item.skip()
        item = item.skip()
        item = item.shift(1, terms.from_string('largest(_, _)'))
        item = item.lift(0, 2)
        item = item.shift(1, terms.from_string('population(_, _)'))
        item = item.coref(1, 1, 0, 1)
        item = item.coref(0, 1, 0, 2)
        item = item.drop(0, 2)
        item = item.drop(0, 2)
        item = item.finish()
        item = item.idle()
        self.assertEqual(len(item.stack), 1)
        self.assertTrue(item.queue.is_empty())
        self.assertTrue(item.is_finished())
        self.assertTrue(item.stack.head.term.equivalent(terms.from_string(
            'answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')))
