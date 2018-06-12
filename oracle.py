import parseitems


def item_hash(item):
    return hash(str(item))


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
    initial = parseitems.initial(words)
    hashes = {item_hash(initial)}
    beam = [initial]
    rejector = Rejector(target_mr)
    while any(not item.finished for item in beam):
        successors = [s for item in beam for s in item.successors()]
        beam = []
        for succ in successors:
            succ_hash = item_hash(succ)
            if succ_hash not in hashes and not rejector.reject(succ):
                beam.append(succ)
                hashes.add(succ_hash)
    if not beam:
        raise ValueError('no action sequence found')
    for item in beam[0].item_sequence():
        print(item)
    return beam[0].action_sequence()
