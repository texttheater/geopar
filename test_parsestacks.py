import parsestacks
import terms
import unittest


class ParseStackTestCase(unittest.TestCase):

    def test_lift(self):
        se1 = parsestacks.new_element(terms.from_string('a(A)'))
        se0 = parsestacks.new_element(terms.from_string('b(B)'))
        se = se0.lift(0, 1, se1)
        ss0 = se.mr.at_address(se.secstack[0])
        ss1 = se.mr
        mr = terms.from_string('a(A)')
        self.assertTrue(ss0.equivalent(mr))
        mr = terms.from_string('b(a(A))')
        self.assertTrue(ss1.equivalent(mr))
        se2 = parsestacks.new_element(terms.from_string('c(C)'))
        se = se.lift(1, 1, se2)
        ss0 = se.mr.at_address(se.secstack[0])
        ss1 = se.mr.at_address(se.secstack[1])
        ss2 = se.mr
        mr = terms.from_string('c(C)')
        self.assertTrue(ss0.equivalent(mr))
        mr = terms.from_string('a(A)')
        self.assertTrue(ss1.equivalent(mr))
        mr = terms.from_string('b((c(C),a(A)))')
        self.assertTrue(ss2.equivalent(mr))

        

