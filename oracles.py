#!/usr/bin/env python3


import oracle
import sys
import terms


if __name__ == '__main__':
    for line in sys.stdin:
        term = terms.from_string(line)
        words = tuple(str(w) for w in term.args[0].elements)
        mr = term.args[1]
        print(' '.join(words))
        print(mr.to_string())
        for action in oracle.action_sequence(words, mr):
            print(action)
        print()
