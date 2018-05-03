import terms


# Maps (multi)words to possible lexical MRs
# TODO this is a stub, many more lexicon entries are needed
_word_term_map = {
    ('adjacent',): (
        'next_to(_,_)',
    ),
    ('alaska',): (
        'const(_,stateid(alaska))',
    ),
    ('biggest',): (
        'largest(_,_)',
        'longest(_,_)',
    ),
}


def meanings(word):
    """Returns the known meanings of a word.
    """
    if word in _word_term_map:
        return (terms.string2term(s) for s in _word_term_map[word])
    return ()
