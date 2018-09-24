import collections
import config
import geoquery
import json
import lexicon
import os
import random
import terms


def read_geoquery_file(path):
    result = []
    with open(path) as f:
        for line in f:
            term = terms.from_string(line)
            words = [str(w) for w in term.args[0].elements]
            mr = term.args[1]
            result.append((words, mr))
    return result


def read_oracle_file(path):
    result = []
    with open(path) as f:
        for line in f:
            line = json.loads(line)
            words = line['words']
            actions = [tuple(a) for a in line['actions']]
            result.append((words, actions))
    return result


def geo880_train():
    path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-train')
    return read_geoquery_file(path)

 
def geo880_test():
    path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-test')
    return read_geoquery_file(path)


def geo880_train_val():
    """Returns a random train-val split from the data.

    Includes 60 validation examples and 539 training oracles.
    """
    examples = geo880_train()
    oracles = read_oracle_file('oracles.json')
    combined = list(zip(examples, oracles))
    random.shuffle(combined)
    train_examples = [example for example, oracle in combined[60:]]
    train_oracles = [oracle for example, oracle in combined[60:]]
    voc = Vocabulary(symbols(train_examples), 2)
    val_examples = [example for example, oracle in combined[:60]]
    return train_oracles, voc, val_examples


def symbols(examples):
    for example in examples:
        words, mr = example
        # Words
        yield from words
        # Functor names and predicate classes
        for term in lexicon.lexical_subterms(mr):
            functor_name = geoquery.term2functor_name(term)
            yield functor_name
            yield geoquery.pred_class(functor_name)
        # Lexical terms
        for term in lexicon.lexical_subterms(mr):
            yield term.to_string()
    for i in range(2): # HACK: add everything else twice so it makes the min_freq cut
        # Action types
        for i in range(2):
            yield 'idle'
            yield 'finish'
            yield 'lift'
            yield 'drop'
            yield 'sdrop'
            yield 'pop'
            yield 'coref'
            yield 'shift'
            yield 'skip'
        # Numbers
        for i in range(2):
            yield from range(0, max(5, config.MAX_TOKEN_LENGTH + 1))    


class Vocabulary:

    def __init__(self, train_data, min_freq=10):
        '''Creates a vocabulary from training data.

        Arguments:
        train_data -- the training data as a sequence of occurrences of
        vocabulary items
        min_freq -- minimum frequency of a vocabulary item in train_data; less
        frequent characters will be treated as unknown
        '''
        counter = collections.Counter(train_data)
        self._w2i = {'__UNKNOWN__': 0, None: 1}
        self._i2w = ['__UNKNOWN__', None]
        for char, freq in counter.items():
            if freq >= min_freq:
                self._w2i[char] = len(self._w2i)
                self._i2w.append(char)

    def w2i(self, word):
        '''Returns the int ID for the given word, or 0 if unknown.'''
        return self._w2i.get(word, 0)

    def i2w(self, word_id):
        '''Returns the word for the given ID.'''
        return self._i2w[word_id]

    def __len__(self):
        return len(self._i2w)
