"""Implements some constraints on well-formed GeoQuery terms.
"""


import augment
import config
import terms


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


def term2functor_name(term):
    if isinstance(term, terms.ConjunctiveTerm):
        term = term.conjuncts[0]
    if term is None:
        return None
    return term.functor_name


def pred_class(functor_name):
    if functor_name in ('most', 'fewest'):
        return 'superlative_count'
    if functor_name in ('largest', 'highest', 'longest', 'lowest', 'shortest', 'smallest'):
        return 'superlative'
    if functor_name in ('sum', 'count'):
        return 'aggregate'
    if functor_name == 'answer':
        return 'answer'
    if functor_name == 'const':
        return 'const'
    return 'other'
