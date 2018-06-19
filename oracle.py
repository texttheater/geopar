import parseitems


def item_id(item):
    return str(item)


class Rejector:

    def __init__(self, target_mr):
        self.target_mr = target_mr
        self.fragments = list(target_mr.fragments())

    def reject(self, item, siblings=None):
        if item.finished:
            return not item.stack.head.equivalent(self.target_mr)
        # TODO enforce consistency across stack elements?
        for term in item.stack:
            if not any(term.subsumes_without_identification(f) for f in self.fragments):
                return True
        return False


def action_sequence(words, target_mr):
    """Looks for action sequences that lead from words to target_mr.

    Returns the first that it finds.
    """
    beam = parseitems.Beam(words, target_mr)
    while any(not item.finished for item in beam.items):
        beam.advance()
    if not beam.items:
        raise ValueError('no action sequence found')
    for item in beam.items[0].item_sequence():
        print(item)
    return beam.items[0].action_sequence()
