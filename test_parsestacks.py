import parsestacks
import terms
import unittest


class StackElementsTestCase(unittest.TestCase):

    def test_stack(self):
        term = terms.from_string('a(A, B)')
        se = parsestacks.StackElement(term)
        # Dropping into [0]:
        term = terms.from_string('b(C, D)')
        se = se.drop(0, 2, term)
        result = terms.from_string('a(A, b(C, D))')
        self.assertTrue(se.term.equivalent(result))
        # Dropping into [1]:
        term = terms.from_string('c(E, F)')
        se = se.drop(1, 2, term)
        result = terms.from_string('a(A, b(C, c(E, F)))')
        self.assertTrue(se.term.equivalent(result))
        # Dropping into [2]:
        term = terms.from_string('d(G, H)')
        se = se.drop(2, 2, term)
        result = terms.from_string('a(A, b(C, (c(E, F), d(G, H))))')
        self.assertTrue(se.term.equivalent(result))
        # Dropping into [0] again:
        term = terms.from_string('e(I, J)')
        se = se.drop(0, 1, term)
        result = terms.from_string('a(e(I, J), b(C, (c(E, F), d(G, H))))')
        self.assertTrue(se.term.equivalent(result))
        # Lifting into [0]:
        term = terms.from_string('f(K, L)')
        se = se.lift(0, 1, term)
        result = terms.from_string('a((f(K, L), e(I, J)), b(C, (c(E, F), d(G, H))))')
        self.assertTrue(se.term.equivalent(result))
        # Dropping into [2] after address change:
        term = terms.from_string('g(M, N)')
        se = se.lift(2, 2, term)
        result = terms.from_string('a((f(K, L), e(I, g(M, N))), b(C, (c(E, F), d(G, H))))')
        self.assertTrue(se.term.equivalent(result))
        # Lifting into [1]:
        term = terms.from_string('h(O, P)')
        se = se.lift(1, 1, term)
        result = terms.from_string('a((f(K, L), e(I, g(h(O, P), N))), b(C, (c(E, F), d(G, H))))')
        self.assertTrue(se.term.equivalent(result))
