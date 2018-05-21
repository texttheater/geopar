import items
import terms
import unittest


class ItemsTestCase(unittest.TestCase):

    def test_items_example1(self):
        """Tests the implementation of the parsing actions.

        This test starts with the initial item for the example from the lecture
        notes (Table 1), applies the parsing actions from that example and
        succeeds if the """
        item = items.initial_item(('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population'))
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
        self.assertTrue(item.stack[0].equivalent(terms.from_string(
            'capital(S, C), largest(P, (state(S), population(S, P)))')))
