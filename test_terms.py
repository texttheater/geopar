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

    def test_subterms(self):
        term = terms.from_string(
            'answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
        subterms = list(term.subterms())
        self.assertEqual(len(subterms), 14)

    def test_subsumes(self):
        self.assertTrue(
            terms.from_string('X').subsumes(
            terms.from_string('Y')))
        self.assertTrue(
            terms.from_string('X').subsumes(
            terms.from_string('a')))
        self.assertFalse(
            terms.from_string('a').subsumes(
            terms.from_string('X')))
        self.assertTrue(
            terms.from_string('a').subsumes(
            terms.from_string('a')))
        self.assertFalse(
            terms.from_string('a').subsumes(
            terms.from_string('b')))
        self.assertTrue(
            terms.from_string('a(A, B)').subsumes(
            terms.from_string('a(C, C)')))
        self.assertFalse(
            terms.from_string('a(C, C)').subsumes(
            terms.from_string('a(A, B)')))
        self.assertTrue(
            terms.from_string('a(A, (b(B), C))').subsumes(
            terms.from_string('a(X, (b(X), c(X)))')))
        self.assertFalse(
            terms.from_string('a(X, (b(X), c(X)))').subsumes(
            terms.from_string('a(D, (b(D), C))')))
        self.assertTrue(
            terms.from_string('a(A)').subsumes(
            terms.from_string('(a(A), b(B))')))
        self.assertTrue(
            terms.from_string('(a(A), b(B))').subsumes(
            terms.from_string('(a(A), b(B), c(C))')))
        self.assertFalse(
            terms.from_string('(a(A), b(B))').subsumes(
            terms.from_string('(a(A), c(B))')))
        self.assertFalse(
            terms.from_string('(a(A), b(B))').subsumes(
            terms.from_string('a(A)')))

    def test_equivalent(self):
        self.assertTrue(
            terms.from_string('X').equivalent(
            terms.from_string('Y')))
        self.assertFalse(
            terms.from_string('X').equivalent(
            terms.from_string('a')))
        self.assertFalse(
            terms.from_string('a').equivalent(
            terms.from_string('X')))
        self.assertTrue(
            terms.from_string('a').equivalent(
            terms.from_string('a')))
        self.assertFalse(
            terms.from_string('a').equivalent(
            terms.from_string('b')))
        self.assertFalse(
            terms.from_string('a(A, B)').equivalent(
            terms.from_string('a(C, C)')))
        self.assertFalse(
            terms.from_string('a(C, C)').equivalent(
            terms.from_string('a(A, B)')))
        self.assertFalse(
            terms.from_string('a(A, (b(B), C))').equivalent(
            terms.from_string('a(X, (b(X), c(X)))')))
        self.assertFalse(
            terms.from_string('a(X, (b(X), c(X)))').equivalent(
            terms.from_string('a(D, (b(D), C))')))
        self.assertTrue(
            terms.from_string('a(A, (b(B), C))').equivalent(
            terms.from_string('a(D, (b(E), F))')))

    def test_string_roundtrip(self):
        t1 = terms.from_string('a(A, A)')
        t2 = terms.from_string('a(B, B)')
        self.assertTrue(t1.equivalent(t2))
        t1 = t1.to_string()
        t1 = terms.from_string(t1)
        self.assertTrue(t1.equivalent(t2))
