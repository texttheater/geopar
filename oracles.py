#!/usr/bin/env python3


import augment
import fileinput
import json
import oracle
import sys
import terms


def unaugment(action):
    if action[0] == 'shift':
        lst = terms.from_string(action[2])
        if isinstance(lst, terms.ComplexTerm):
            lst.functor_name = augment.unaugment(lst.functor_name)
        action = (action[0], action[1], lst.to_string())
    return action
        


if __name__ == '__main__':
    for line in fileinput.input():
        term = terms.from_string(line)
        words = tuple(str(w) for w in term.args[0].elements)
        mr = term.args[1]
        actions = oracle.action_sequence(words, mr)
        print(json.dumps({'words': words, 'actions': [unaugment(a) for a in actions]}))
