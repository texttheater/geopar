"""Implements some constraints on well-formed GeoQuery terms.
"""


import augment
import config


def coref_allowed(term, arg_num):
    name = augment.unaugment(term.functor_name)
    if name in ('most', 'fewest'):
        return arg_num in (1, 2)
    if name in ('sum', 'count'):
        return arg_num in (1, 3)
    if name in ('largest', 'highest', 'longest', 'lowest', 'shortest', 'smallest', 'answer'):
        return arg_num == 1
    return True


def integrate_allowed(term, arg_num):
    name = augment.unaugment(term.functor_name)
    if name in ('most', 'fewest'):
        return arg_num == 3
    if name in ('sum', 'count'):
        return arg_num == 2
    if name in ('largest', 'highest', 'longest', 'lowest', 'shortest', 'smallest', 'answer'):
        return arg_num == 2
    if name == '\+':
        return arg_num == 1
    if len(name) == 1: # single-letter names for testing
        return True
    return False


def skip_allowed(queue, lex):
    # This is turning into a farce:
    if queue.head in ('is', 'of', 'with', 'city', 'in', 'have', 'has', 'state', 'least', 'river', 'rivers', 'through', 'square', 'kilometers', 'whose', 'major', 'total', 'country', 'neighboring', 'for'):
        return True
    for token_length in range(1, config.MAX_TOKEN_LENGTH + 1):
        try:
            token = tuple(queue[i] for i in range(token_length))
        except IndexError:
            break
        if tuple(lex.meanings(token)):
            return False
    return True
