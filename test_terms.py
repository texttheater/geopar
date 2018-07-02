import lstack
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
        self.assertFalse(
            terms.from_string('a(A)').subsumes(
            terms.from_string('(a(A), b(B))')))
        self.assertFalse(
            terms.from_string('(a(A), b(B))').subsumes(
            terms.from_string('(a(A), b(B), c(C))')))
        self.assertFalse(
            terms.from_string('(a(A), b(B))').subsumes(
            terms.from_string('(a(A), c(B))')))
        self.assertFalse(
            terms.from_string('(a(A), b(B))').subsumes(
            terms.from_string('a(A)')))
        self.assertFalse(
            terms.from_string('answer(A,(capital(B,A),largest(C,(state(A),population(D,E)))))').subsumes(
            terms.from_string('answer(C,(capital(S,C),largest(P,(state(S),population(S,P)))))')))
        self.assertFalse(
            terms.from_string('answer(A,(state(A),population(D,E)))').subsumes(
            terms.from_string('answer(C,(state(S),population(S,P)))')))


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
        self.assertFalse(
            terms.from_string('answer(A,(capital(B,A),largest(C,(state(A),population(D,E)))))').equivalent(
            terms.from_string('answer(C,(capital(S,C),largest(P,(state(S),population(S,P)))))')))

    def test_string_roundtrip(self):
        t1 = terms.from_string('a(A, A)')
        t2 = terms.from_string('a(B, B)')
        self.assertTrue(t1.equivalent(t2))
        t1 = t1.to_string()
        t1 = terms.from_string(t1)
        self.assertTrue(t1.equivalent(t2))

    def test_left_address(self):
        t = terms.from_string('answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
        s = t.left_address([])
        self.assertTrue(s.equivalent(t))
        s = t.left_address([1])
        self.assertTrue(s.equivalent(terms.from_string('C')))
        s = t.left_address([2])
        self.assertTrue(s.equivalent(terms.from_string('capital(S, C)')))
        s = t.left_address([2, 1])
        self.assertTrue(s.equivalent(terms.from_string('S')))
        s = t.left_address([2, 2])
        self.assertTrue(s.equivalent(terms.from_string('C')))

    def test_right_address(self):
        t = terms.from_string('answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
        s = t.right_address([])
        self.assertTrue(s.equivalent(t))
        s = t.right_address([1])
        self.assertTrue(s.equivalent(terms.from_string('C')))
        s = t.right_address([2])
        self.assertTrue(s.equivalent(terms.from_string('largest(P, (state(S), population(S, P)))')))
        s = t.right_address([2, 1])
        self.assertTrue(s.equivalent(terms.from_string('P')))
        s = t.right_address([2, 2])
        self.assertTrue(s.equivalent(terms.from_string('population(S, P)')))
        s = t.right_address([2, 2, 1])
        self.assertTrue(s.equivalent(terms.from_string('S')))
        s = t.right_address([2, 2, 2])
        self.assertTrue(s.equivalent(terms.from_string('P')))

    def test_fragments1(self):
        term = terms.from_string('(a,b,c,d,e)')
        gold = ['a', 'b', 'c', 'd', 'e', '(a,b)', '(a,b,c)', '(a,b,c,d)',
                '(a,b,c,d,e)', '(b,c,d,e)', '(c,d,e)', '(d,e)']
        pred = [f.to_string() for f in term.fragments()]
        self.assertEqual(pred, gold)

    def test_fragments2(self):
        term = terms.from_string('a(a,(b,c))')
        gold = ['a', 'b', 'c', '(b,c)', 'a(a,b)', 'a(a,c)', 'a(a,(b,c))']
        pred = [f.to_string() for f in term.fragments()]
        self.assertEqual(pred, gold)

    def test_fragments3(self):
        term = terms.from_string('a(A,(b,c))')
        gold = ['A', 'b', 'c', '(b,c)', 'a(A,b)', 'a(A,c)', 'a(A,(b,c))']
        pred = [f.to_string() for f in term.fragments()]
        self.assertEqual(pred, gold)

    def test_subsumes_without_identification(self):
        t1 = terms.from_string('a(A,B)')
        t2 = terms.from_string('a(A,B)')
        self.assertTrue(t1.subsumes_without_identification(t2))
        t1 = terms.from_string('a(A,B)')
        t2 = terms.from_string('a(A,A)')
        self.assertFalse(t1.subsumes_without_identification(t2))

    def test_secstack(self):
        t1 = terms.from_string('a(A)')
        t2 = terms.from_string('b(B)')
        t3 = terms.ConjunctiveTerm((t1, t2))
        secstack = lstack.stack()
        self.assertEqual(t3.to_string(secstack=secstack), '(a(A),b(B))')
        secstack = lstack.stack((t1,))
        self.assertEqual(t3.to_string(secstack=secstack), '([0]a(A),b(B))')
        secstack = lstack.stack((t2,))
        self.assertEqual(t3.to_string(secstack=secstack), '(a(A),[0]b(B))')
        secstack = lstack.stack((t2,t1))
        self.assertEqual(t3.to_string(secstack=secstack), '([1]a(A),[0]b(B))')
