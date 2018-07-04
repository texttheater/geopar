import parseitems


class Rejector:

    def __init__(self, target_mr):
        self.target_mr = target_mr
        self.fragments = list(f for s in target_mr.subterms() for f in s.fragments())

    def reject(self, item, siblings=None):
        if item.finished:
            return not item.stack.head.mr.equivalent(self.target_mr)
        # TODO enforce consistency across stack elements?
        for se in item.stack:
            if not any(se.mr.subsumes(f) for f in self.fragments):
                return True
        return False


def action_sequence(words, target_mr):
    """Looks for action sequences that lead from words to target_mr.

    Returns the first that it finds.
    """
    items = [parseitems.initial(words)]
    rejector = Rejector(target_mr)
    seen = {str(items[0])}
    while any(not item.finished for item in items):
        #print(len(items))
        successors = [s for i in items for s in i.successors()]
        items = []
        for s in successors:
            if (s.action == ('idle',) or not str(s) in seen) \
                and (not rejector.reject(s)):
                items.append(s)
                seen.add(str(s))
    if not items:
        raise ValueError('no action sequence found')
    return items[0].action_sequence()
