import parseitems
import parsestacks
import random


def accept(item, target_mr):
    if item.finished:
        return item.stack.head.term.equivalent(target_mr)
    bindings = {}
    for se in item.stack:
        if not target_mr.contains_subsumee(se.term, bindings):
            return False
    return True


def action_sequence(words, target_mr):
    beam = [parseitems.initial(words)]
    while True:
        # Generate successors:
        beam = [s for i in beam for s in i.successors()]
        # Keep only acceptable ones:
        beam = [i for i in beam if accept(i, target_mr)]
        # HACK: always do coref/drop/lift before skip
        if any(i.actions.head[0] in ('shift', 'coref', 'drop', 'lift') for i in beam):
            beam = [i for i in beam if i.actions.head[0] != 'skip']
        # If beam empty, error:
        if not beam:
            raise ValueError('no action sequence found')
        # Have we found a sequence?
        for item in beam:
            if item.finished:
                return item.action_sequence()

