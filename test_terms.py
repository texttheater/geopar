import terms
import unittest


class TermsTestCase(unittest.TestCase):

    def test_replace(self):
        before = terms.from_string('a(A, B, (C, A))')
        after = terms.from_string('a(X, X, (Y, X))')
        self.assertFalse(before.equivalent(after))
        A = before.args[0]
        B = before.args[1]
        now = before.replace(A, B)
        self.assertTrue(now.equivalent(after))

    def test_integrate(self):
        # Integrate into variable arg at address []
        t1 = terms.from_string('a(A, B)')
        t2 = terms.from_string('b(C, D)')
        t3, address = t1.integrate([], 2, t2)
        self.assertEqual(address, [(2, 1)])
        self.assertTrue(t3.equivalent(terms.from_string('a(A, b(C, D))')))
        # Integrate into one conjunct at address []
        t4 = terms.from_string('c(E, F)')
        t5, address = t3.integrate([], 2, t4)
        self.assertEqual(address, [(2, 2)])
        self.assertTrue(t5.equivalent(terms.from_string('a(A, (b(C, D), c(E, F)))')))
        # Integrate into variable at a nonempty address
        t6 = terms.from_string('d(G, H)')
        t7, address = t5.integrate([(2, 1)], 2, t6)
        self.assertEqual(address, [(2, 1), (2, 1)])
        self.assertTrue(t7.equivalent(terms.from_string('a(A, (b(C, d(G, H)), c(E, F)))')))
        # Integrate into one conjunct at a nonempty address
        t8 = terms.from_string('e(I, J)')
        t9, address = t7.integrate([(2,1)], 2, t8)
        self.assertEqual(address, [(2, 1), (2, 2)])
        self.assertTrue(t9.equivalent(terms.from_string('a(A, (b(C, (d(G, H), e(I, J))), c(E, F)))')))
        # Integrate into two conjuncts at address []
        t10 = terms.from_string('f(K, L)')
        t11, address = t9.integrate([], 2, t10)
        self.assertEqual(address, [(2, 3)])
        self.assertTrue(t11.equivalent(terms.from_string('a(A, (b(C, (d(G, H), e(I, J))), c(E, F), f(K, L)))')))
        # Integreate into two conjuncts at a nonempty address
        t12 = terms.from_string('g(M, N)')
        t13, address = t11.integrate([(2, 1)], 2, t12)
        self.assertEqual(address, [(2, 1), (2, 3)])
        self.assertTrue(t13.equivalent(terms.from_string('a(A, (b(C, (d(G, H), e(I, J), g(M, N))), c(E, F), f(K, L)))')))
