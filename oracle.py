import collections
import lexicon
import parseitems
import util


def initial_beam(words, target_mr):
    items = [parseitems.initial(words)]
    rejector = Rejector(target_mr)
    seen = set()
    return Beam(items, rejector, seen)


class Beam:

    def __init__(self, items, rejector, seen):
        self.items = items
        self.rejector = rejector
        self.seen = seen

    def next(self):
        next_items = []
        for item in self.items:
            successors = item.successors()
            successors = [s for s in successors if self.check_rejector(s)]
            # TODO fix the siblings check
            #successors = [s for s in successors if self.check_siblings(s, successors)]
            successors = [s for s in successors if self.check_seen(s)]
            next_items.extend(successors)
        return Beam(next_items, self.rejector, self.seen)

    def check_rejector(self, item):
        return not self.rejector.reject(item)

    def check_siblings(self, item, siblings):
        # TODO this probably needs to be even more restrictive
        if item.action[0] in ('pop', 'skip', 'shift') and any(
                s.action[0] in ('coref', 'lift', 'slift', 'drop', 'sdrop') for s in siblings):
            return False
        if item.action[0] == 'pop' and any(
                s.action[0] in ('skip', 'shift') for s in siblings):
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

    def reject(self, item, siblings=None):
        if item.finished:
            return not item.stack.head.mr.equivalent(self.target_mr)
        elements = collections.Counter(l.to_string() for se in item.stack for l in lexicon.lexical_subterms(se.mr))
        if not util.issubset(elements, self.elements):
            return True
        # TODO enforce consistency across stack elements?
        for se in item.stack:
            if not any(se.mr.subsumes(f) for f in self.fragments):
                return True
        return False


def action_sequence(words, target_mr):
    """Looks for action sequences that lead from words to target_mr.

    Returns the first that it finds.
    """
    beam = initial_beam(words, target_mr)
    while any(not item.finished for item in beam.items):
        print(len(beam.items))
        beam = beam.next()
    if not beam.items:
        raise ValueError('no action sequence found')
    return beam.items[0].action_sequence()
