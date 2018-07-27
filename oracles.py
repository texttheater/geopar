#!/usr/bin/env python3


import augment
import fileinput
import oracle
import sys
import terms


if __name__ == '__main__':
    for line in fileinput.input():
        term = terms.from_string(line)
        words = tuple(str(w) for w in term.args[0].elements)
        mr = term.args[1]
        print(' '.join(words))
        print(mr.to_string())
        for action in oracle.action_sequence(words, mr):
            if action[0] == 'confirm':
                lst = terms.from_string(action[1])
                if isinstance(lst, terms.ComplexTerm):
                    lst.functor_name = augment.unaugment(lst.functor_name)
                action = (action[0], action[1], lst.to_string())
            print(action)
        print()
