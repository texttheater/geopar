import terms
import unittest


class TermsTestCase(unittest.TestCase):

    def test_replace(self):
        before = terms.string2term('a(A, B, (C, A))')
        after = terms.string2term('a(X, X, (Y, X))')
        self.assertFalse(before.equivalent(after))
        A = before.args[0]
        B = before.args[1]
        now = before.replace(A, B)
        self.assertTrue(now.equivalent(after))

