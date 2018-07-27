import lstack
import unittest


class LinkedStackTestCase(unittest.TestCase):

    def test_lstack(self):
        s = lstack.stack()
        t = s.push('a')
        u = t.push('b')
        self.assertEqual(u.pop(), t)
        self.assertEqual(t.pop(), s)
        with self.assertRaises(IndexError):
            s.pop()
        with self.assertRaises(IndexError):
            s[0]
        self.assertEqual(t[0], 'a')
        self.assertEqual(u[0], 'b')
        self.assertEqual(u[1], 'a')
        self.assertTrue(s.is_empty())
        self.assertEqual(len(s), 0)
        self.assertFalse(t.is_empty())
        self.assertEqual(len(t), 1)
        self.assertFalse(u.is_empty())
        self.assertEqual(len(u), 2)
        l = list(u)
        self.assertEqual(l, ['b', 'a'])

    def test_list_roundtrip(self):
        l = ['a', 'b', 1, 'c', 2, 3]
        s = lstack.stack(l)
        l2 = list(s)
        self.assertEqual(l, l2)

    def test_index(self):
        s = lstack.stack((1, 2, 3))
        self.assertEqual(s.index(1), 0)
        self.assertEqual(s.index(2), 1)
        self.assertEqual(s.index(3), 2)
        with self.assertRaises(ValueError):
            s.index(0)
        with self.assertRaises(ValueError):
            s.index(4)
