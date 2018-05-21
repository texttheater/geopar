import collections
import os
import terms


def read_lexicon(path):
    word_term_map = collections.defaultdict(list)
    with open(path) as f:
        for line in f:
            if not line.split() or line.startswith('#'):
                continue
            mr, word = line.rsplit(maxsplit=1)
            tokens = tuple(word.split(','))
            word_term_map[tokens].append(mr)
    return word_term_map


_word_term_map = read_lexicon(os.path.join(os.path.dirname(__file__), 'lexicon.txt'))


def meanings(word):
    """Returns the known meanings of a word.
    """
    if word in _word_term_map:
        return (terms.from_string(s) for s in _word_term_map[word])
    return ()
