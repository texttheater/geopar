import data
import unittest


class DataTest(unittest.TestCase):

    def test_vocabulary(self):
        examples = data.geo880_train()
        voc = data.Vocabulary(data.symbols(examples), 2)
        # frequent words
        self.assertIn('state', voc._w2i)
        self.assertIn('cities', voc._w2i)
        # infrequent words
        self.assertNotIn('lie', voc._w2i)
        self.assertNotIn('adjoin', voc._w2i)
        # functor names
        self.assertIn('most', voc._w2i)
        self.assertIn('fewest', voc._w2i)
        self.assertIn('largest', voc._w2i)
        self.assertIn('highest', voc._w2i)
        self.assertIn('longest', voc._w2i)
        self.assertIn('lowest', voc._w2i)
        self.assertIn('shortest', voc._w2i)
        self.assertIn('smallest', voc._w2i)
        self.assertIn('sum', voc._w2i)
        self.assertIn('count', voc._w2i)
        self.assertIn('answer', voc._w2i)
        self.assertIn('const', voc._w2i)
        self.assertIn('state', voc._w2i)
        self.assertIn('city', voc._w2i)
        self.assertIn('river', voc._w2i)
        self.assertIn('capital', voc._w2i)
        # predicate classes
        self.assertIn('superlative_count', voc._w2i)
        self.assertIn('superlative', voc._w2i)
        self.assertIn('aggregate', voc._w2i)
        self.assertIn('answer', voc._w2i)
        self.assertIn('const', voc._w2i)
        self.assertIn('other', voc._w2i)
        # frequent lexical terms
        self.assertIn('city(A)', voc._w2i)
        self.assertIn('loc(A,B)', voc._w2i)
        self.assertIn('const(A,stateid(virginia))', voc._w2i)
        # infrequent lexical terms
        self.assertNotIn("const(A,stateid('north dakota'))", voc._w2i)
        self.assertNotIn("const(A,cityid(boston,ma))", voc._w2i)
        # action types
        self.assertIn('idle', voc._w2i)
        self.assertIn('finish', voc._w2i)
        self.assertIn('lift', voc._w2i)
        self.assertIn('drop', voc._w2i)
        self.assertIn('sdrop', voc._w2i)
        self.assertIn('pop', voc._w2i)
        self.assertIn('coref', voc._w2i)
        self.assertIn('shift', voc._w2i)
        self.assertIn('skip', voc._w2i)
        # Numbers
        self.assertIn(0, voc._w2i)
        self.assertIn(1, voc._w2i)
        self.assertIn(2, voc._w2i)
        self.assertIn(3, voc._w2i)
        self.assertIn(4, voc._w2i)
        # None
        self.assertIn(None, voc._w2i)
        # unknown symbol
        self.assertIn('__UNKNOWN__', voc._w2i)
