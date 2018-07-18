import augment
import collections
import lexicon
import parseitems
import random
import util


def initial_beam(words, target_mr, lex):
    items = [parseitems.initial(words)]
    rejector = Rejector(target_mr)
    seen = set()
    return Beam(items, rejector, seen, lex)


class Beam:

    def __init__(self, items, rejector, seen, lex):
        self.items = items
        self.rejector = rejector
        self.seen = seen
        self.lex = lex

    def next(self):
        next_items = []
        for item in self.items:
            successors = item.successors(self.lex)
            successors = [s for s in successors if self.check_rejector(s)]
            # TODO fix the siblings check
            successors = [s for s in successors if self.check_siblings(s, successors)]
            successors = [s for s in successors if self.check_seen(s)]
            next_items.extend(successors)
        return Beam(next_items, self.rejector, self.seen, self.lex)

    def check_rejector(self, item):
        return not self.rejector.reject(item)

    def check_siblings(self, item, siblings):
        #for sibling in siblings:
        #    print('~', sibling)
        #print()
        # These tests don't work:
        # TODO this probably needs to be even more restrictive
        #if item.action[0] in ('pop', 'skip', 'shift') and any(
        #        s.action[0] in ('coref', 'lift', 'slift', 'drop', 'sdrop') for s in siblings):
        #    return False
        #if item.action[0] == 'pop' and any(
        #        s.action[0] in ('skip', 'shift') for s in siblings):
        #    return False
        if item.action[0] in ('skip', 'shift') and any(
            s.action[0] in ('drop', 'lift', 'sdrop', 'slift') for s in siblings):
            return False
        return True

    def check_seen(self, item):
        if item.action[0] == 'idle':
            return True
        string = str(item)
        if string in self.seen:
            return False
        self.seen.add(string)
        return True


class Rejector:

    def __init__(self, target_mr):
        self.target_mr = target_mr
        self.fragments = list(f for s in target_mr.subterms() for f in s.fragments())
        self.elements = collections.Counter(l.to_string() for l in lexicon.lexical_subterms(target_mr))

    def reject(self, item):
        # TODO can only drop/lift/sdrop/slift something that already has all variable bindings with its environment
        if item.finished:
            return not item.stack.head.mr.equivalent(self.target_mr)
        # predicate bag check (TODO: this can be better, like making sure stack and queue elements add up to the needed ones)
        elements = collections.Counter(l.to_string() for se in item.stack for l in lexicon.lexical_subterms(se.mr))
        if not util.issubset(elements, self.elements):
            return True
        # fragment check (false negatives (and positives?) unless mr is augmented!)
        fragments = tuple(find_fragment(se.mr, self.fragments) for se in item.stack)
        bindings = {}
        for se, fr in zip(item.stack, fragments):
            if not se.mr.subsumes(fr, bindings):
                return True
        return False


def find_fragment(mr, fragments):
    for fr in fragments:
        if mr.equivalent(fr):
            return fr


def action_sequence(words, target_mr):
    """Looks for action sequences that lead from words to target_mr.

    Returns the first that it finds.
    """
    lex = augment.AugmentingLexicon(lexicon.read_lexicon('lexicon.txt'), target_mr)
    beam = initial_beam(words, target_mr.augment(), lex)
    while beam.items:
        print(len(beam.items), random.choice(beam.items))
        beam = beam.next()
        finished = [i for i in beam.items if i.finished]
        if finished:
            return finished[0].action_sequence()
    raise ValueError('no action sequence found')
