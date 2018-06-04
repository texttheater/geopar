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
