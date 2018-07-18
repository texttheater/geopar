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
