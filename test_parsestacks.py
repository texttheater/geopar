import parsestacks
import terms
import unittest


class StackElementsTestCase(unittest.TestCase):

    def test_stack(self):
        term = terms.from_string('a(A, B)')
        se = parsestacks.StackElement(term)
        # Integrating at [0]:
        term = terms.from_string('b(C, D)')
        se = se.drop(0, 2, term)
        result = terms.from_string('a(A, b(C, D))')
        self.assertTrue(se.term.equivalent(result))
        # Integrating at [1]:
        term = terms.from_string('c(E, F)')
        se = se.drop(1, 2, term)
        result = terms.from_string('a(A, b(C, c(E, F)))')
        self.assertTrue(se.term.equivalent(result))
        # Integrating at [2]:
        term = terms.from_string('d(G, H)')
        se = se.drop(2, 2, term)
        result = terms.from_string('a(A, b(C, (c(E, F), d(G, H))))')
        self.assertTrue(se.term.equivalent(result))
        # Integrating at [0] again:
        term = terms.from_string('e(I, J)')
        se = se.drop(0, 1, term)
        result = terms.from_string('a(e(I, J), b(C, (c(E, F), d(G, H))))')
        self.assertTrue(se.term.equivalent(result))
