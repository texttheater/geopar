import augment
import lexicon
import oracle
import parseitems
import terms
import unittest


class ItemsTestCase(unittest.TestCase):

    def test_example1(self):
        words = ('what', 'is', 'the', 'capital', 'of', 'the', 'state', 'with', 'the', 'largest', 'population')
        target_mr = terms.from_string('answer(C, (capital(S, C), largest(P, (state(S), population(S, P)))))')
        actions = [
            ('skip',),
            ('skip',),
            ('skip',),
            ('shift', 1, 'capital_1(A,B)'),
            ('coref', 0, 1, 0, 2),
            ('drop', 2),
            ('skip',),
            ('skip',),
            ('shift', 1, 'state_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('skip',),
            ('skip',),
            ('shift', 1, 'largest_1(A,B)'),
            ('lift', 2),
            ('shift', 1, 'population_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('coref', 1, 1, 0, 2),
            ('sdrop',),
            ('pop',),
            ('pop',),
            ('sdrop',),
            ('pop',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

    def test_example2(self):
        words = ('could', 'you', 'tell', 'me', 'what', 'is', 'the', 'highest',
            'point', 'in', 'the', 'state', 'of', 'oregon', '?')
        target_mr = terms.from_string('answer(A,highest(A,(place(A),loc(A,B),state(B),const(B,stateid(oregon)))))')
        actions = [
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('shift', 1, 'highest_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('drop', 2),
            ('shift', 1, 'place_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('drop', 2),
            ('shift', 1, 'loc_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('skip',),
            ('shift', 1, 'state_1(A)'),
            ('coref', 0, 2, 0, 1),
            ('sdrop',),
            ('skip',),
            ('shift', 1, 'const_1(A,stateid(oregon))'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('skip',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

    def test_example3(self):
        words = ('how', 'many', 'big', 'cities', 'are', 'in', 'pennsylvania', '?')
        actions = [
            ('skip',),
            ('shift', 1, 'count_1(A,B,C)'),
            ('coref', 0, 1, 0, 3),
            ('drop', 2),
            ('shift', 1, 'major_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('drop', 2),
            ('shift', 1, 'city_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('skip',),
            ('shift', 1, 'loc_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('shift', 1, 'const_1(A,stateid(pennsylvania))'),
            ('coref', 0, 2, 0, 1),
            ('sdrop',),
            ('skip',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        target_mr = terms.from_string('answer(A,count(B,(major(B),city(B),loc(B,C),const(C,stateid(pennsylvania))),A))')
        self._test_action_sequence(words, actions, target_mr)

    def test_example4(self):
        words = ('how', 'many', 'rivers', 'do', 'not', 'traverse', 'the', 'state', 'with', 'the', 'capital', 'albany', '?')
        target_mr = terms.from_string('answer(A,count(B,(river(B),\+ (traverse(B,C),state(C),loc(D,C),capital(D),const(D,cityid(albany,_)))),A))')
        actions = [
            ('skip',),
            ('shift', 1, 'count_1(A,B,C)'),
            ('coref', 0, 1, 0, 3),
            ('drop', 2),
            ('shift', 1, 'river_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('drop', 2),
            ('skip',),
            ('shift', 1, '\+_1A'),
            ('sdrop',),
            ('shift', 1, 'traverse_1(A,B)'),
            ('coref', 1, 1, 0, 1),
            ('drop', 1),
            ('skip',),
            ('shift', 1, 'state_1(A)'),
            ('coref', 0, 2, 0, 1),
            ('sdrop',),
            ('shift', 1, 'loc_1(A,B)'),
            ('coref', 0, 1, 0, 2),
            ('sdrop',),
            ('skip',),
            ('shift', 1, 'capital_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('shift', 1, 'const_1(A,cityid(albany,B))'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('skip',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

    def test_example5(self):
        words = ('in', 'what', 'state', 'is', 'mount', 'mckinley', '?')
        target_mr = terms.from_string("answer(A,(loc(B,A),state(A),const(B,placeid('mount mckinley'))))")
        actions = [
            ('shift', 1, 'loc_1(A,B)'),
            ('coref', 0, 1, 0, 2),
            ('drop', 2),
            ('skip',),
            ('shift', 1, 'state_1(A)'),
            ('coref', 0, 2, 0, 1),
            ('sdrop',),
            ('skip',),
            ('shift', 2, "const_1(A,placeid('mount mckinley'))"),
            ('pop',),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('skip',),
            ('pop',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

    def test_example6(self):
        words = ('of', 'the', 'states', 'washed', 'by', 'the', 'mississippi', 'river', 'which', 'has', 'the', 'lowest', 'point', '?')
        target_mr = terms.from_string('answer(A,lowest(B,(state(A),traverse(C,A),const(C,riverid(mississippi)),loc(B,A),place(B))))')
        actions = [
            ('skip',),
            ('skip',),
            ('shift', 1, 'state_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('shift', 1, 'traverse_1(A,B)'),
            ('coref', 0, 1, 0, 2),
            ('skip',),
            ('skip',),
            ('shift', 1, "const_1(A,riverid(mississippi))"),
            ('coref', 0, 1, 0, 1),
            ('skip',),
            ('skip',),
            ('shift', 1, 'loc_1(A,B)'),
            ('skip',),
            ('shift', 1, 'lowest_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('lift', 2),
            ('slift',),
            ('coref', 0, 2, 1, 2),
            ('slift',),
            ('slift',),
            ('shift', 1, 'place_1(A)'),
            ('pop',),
            ('pop',),
            ('pop',),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('pop',),
            ('pop',),
            ('drop', 2),
            ('skip',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

    def test_example7(self):
        words = ('what', 'are', 'the', 'major', 'cities', 'in', 'the', 'states', 'through', 'which', 'the', 'major', 'river', 'in', 'virginia', 'runs', '?')
        target_mr = terms.from_string('answer(A,(major(A),city(A),loc(A,B),state(B),river(C),loc(C,D),const(D,stateid(virginia)),traverse(C,B)))')
        actions = [
            ('skip',),
            ('skip',),
            ('skip',),
            ('shift', 1, 'major_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('drop', 2),
            ('shift', 1, 'city_1(A)'),
            ('coref', 1, 1, 0, 1),
            ('sdrop',),
            ('shift', 1, 'loc_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('skip',),
            ('shift', 1, 'state_1(A)'),
            ('coref', 0, 2, 0, 1),
            ('sdrop',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('skip',),
            ('shift', 1, 'river_1(A)'),
            ('sdrop',),
            ('shift', 1, 'loc_2(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('sdrop',),
            ('shift', 1, 'const_1(A,stateid(virginia))'),
            ('coref', 0, 2, 0, 1),
            ('sdrop',),
            ('shift', 1, 'traverse_1(A,B)'),
            ('pop',),
            ('coref', 0, 1, 0, 1),
            ('pop',),
            ('pop',),
            ('coref', 0, 1, 0, 2),
            ('sdrop',),
            ('skip',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

#    def test_example8(self):
#        words = ('what', 'state', 'borders', 'the', 'least', 'states', 'excluding', 'alaska', 'and', 'excluding', 'hawaii', '?')
#        target_mr = terms.from_string('answer(A,fewest(A,B,(state(A),next_to(A,B),\+const(A,stateid(alaska)),\+const(A,stateid(hawaii)))))')
#        actions = [
#            ('skip',),
#            ('shift', 1, 'state(A)'),
#            ('shift', 1, 'next_to(A,B)'),
#            ('coref', 0, 1, 0, 1),
#            ('skip',),
#            ('shift', 1, 'fewest(A,B,C)'),
#            ('coref', 0, 1, 0, 1),
#            ('coref', 0, 2, 0, 2),
#            ('lift', 3),
#            ('slift',),
#            ('sh
#        ]

    def test_example8(self):
        words = 'which is the lowest point of the states that the mississippi runs through ?'.split()
        target_mr = terms.from_string('answer(A,lowest(B,(place(B),loc(B,A),state(A),const(C,riverid(mississippi)),traverse(C,A))))')
        actions = [
            ('skip',),
            ('skip',),
            ('skip',),
            ('shift', 1, 'lowest_1(A,B)'),
            ('drop', 2),
            ('shift', 1, 'place_1(A)'),
            ('coref', 0, 1, 0, 1),
            ('drop', 2),
            ('shift', 1, 'loc_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('coref', 2, 1, 0, 2),
            ('sdrop',),
            ('skip',),
            ('shift', 1, 'state_1(A)'),
            ('coref', 0, 2, 0, 1),
            ('sdrop',),
            ('skip',),
            ('skip',),
            ('shift', 1, 'const_1(A,riverid(mississippi))'),
            ('sdrop',),
            ('shift', 1, 'traverse_1(A,B)'),
            ('coref', 0, 1, 0, 1),
            ('pop',),
            ('coref', 0, 1, 0, 2),
            ('sdrop',),
            ('skip',),
            ('skip',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('pop',),
            ('finish',),
            ('idle',),
        ]
        self._test_action_sequence(words, actions, target_mr)

    def _test_action_sequence(self, words, actions, target_mr):
        """Tests that the given action sequence is found.

        Tests that given the words and target_mr, the given actions are found
        and allowed by the oracle.
        """
        lex = augment.AugmentingLexicon(lexicon.read_lexicon('lexicon.txt'), target_mr)
        beam = oracle.initial_beam(words, target_mr.augment(), lex)
        item = beam.items[0]
        for action in actions:
            for i in beam.items:
                print(i)
            print()
            #print(item)
            item.successor(action, lex)
            beam = beam.next()
            beam.items = [s for s in beam.items if s.action == action]
            self.assertTrue(beam.items, '{} not applied to {}, or rejected'.format(action, item))
            self.assertEqual(len(beam.items), 1)
            item = beam.items[0]
        self.assertTrue(item.finished)
