"""Implements some constraints on well-formed GeoQuery terms.
"""


import lexicon
import parseitems


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
    if len(term.functor_name) == 1: # single-letter names for testing
        return True
    return False


def skip_allowed(queue):
    return True
