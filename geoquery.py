"""Implements some constraints on well-formed GeoQuery terms.
"""


import lexicon
import config


def coref_allowed(term, arg_num):
    if term.functor_name in ('most', 'fewest'):
        return arg_num in (1, 2)
    if term.functor_name in ('sum', 'count'):
        return arg_num in (1, 3)
    if term.functor_name in ('largest', 'highest', 'longest', 'lowest', 'shortest', 'smallest', 'answer'):
        return arg_num == 1
    return True


def integrate_allowed(term, arg_num):
    if term.functor_name in ('most', 'fewest'):
        return arg_num == 3
    if term.functor_name in ('sum', 'count'):
        return arg_num == 2
    if term.functor_name in ('largest', 'highest', 'longest', 'lowest', 'shortest', 'smallest', 'answer'):
        return arg_num == 2
    if term.functor_name == '\+':
        return arg_num == 1
    if len(term.functor_name) == 1: # single-letter names for testing
        return True
    return False


def skip_allowed(queue):
	# This is turning into a farce:
    if queue.head in ('is', 'of', 'with', 'city', 'in', 'have', 'has', 'state', 'least', 'river', 'rivers', 'through', 'square', 'kilometers', 'whose', 'major', 'total', 'country', 'neighboring', 'for'):
        return True
    for token_length in range(1, config.MAX_TOKEN_LENGTH + 1):
        try:
            token = tuple(queue[i] for i in range(token_length))
        except IndexError:
            break
        if lexicon.meanings(token):
            return False
    return True
