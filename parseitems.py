import geoquery
import lexicon
import lstack
import terms


MAX_TOKEN_LENGTH = 3
POSSIBLE_COREF_ACTIONS = [ # TODO Do we need more? less? Order okay?
    ('coref', (3, 3), (3,)),
    ('coref', (3, 3), (2,)),
    ('coref', (3, 3), (1,)),
    ('coref', (3, 2), (3,)),
    ('coref', (3, 2), (2,)),
    ('coref', (3, 2), (1,)),
    ('coref', (3, 1), (3,)),
    ('coref', (3, 1), (2,)),
    ('coref', (3, 1), (1,)),
    ('coref', (2, 3), (3,)),
    ('coref', (2, 3), (2,)),
    ('coref', (2, 3), (1,)),
    ('coref', (2, 2), (3,)),
    ('coref', (2, 2), (2,)),
    ('coref', (2, 2), (1,)),
    ('coref', (2, 1), (3,)),
    ('coref', (2, 1), (2,)),
    ('coref', (2, 1), (1,)),
    ('coref', (1, 3), (3,)),
    ('coref', (1, 3), (2,)),
    ('coref', (1, 3), (1,)),
    ('coref', (1, 2), (3,)),
    ('coref', (1, 2), (2,)),
    ('coref', (1, 2), (1,)),
    ('coref', (1, 1), (3,)),
    ('coref', (1, 1), (2,)),
    ('coref', (1, 1), (1,)),
#    ('coref', (3,), (3, 3)),
#    ('coref', (2,), (3, 3)),
#    ('coref', (1,), (3, 3)),
#    ('coref', (3,), (3, 2)),
#    ('coref', (2,), (3, 2)),
#    ('coref', (1,), (3, 2)),
#    ('coref', (3,), (3, 1)),
#    ('coref', (2,), (3, 1)),
#    ('coref', (1,), (3, 1)),
#    ('coref', (3,), (2, 3)),
#    ('coref', (2,), (2, 3)),
#    ('coref', (1,), (2, 3)),
#    ('coref', (3,), (2, 2)),
#    ('coref', (2,), (2, 2)),
#    ('coref', (1,), (2, 2)),
#    ('coref', (3,), (2, 1)),
#    ('coref', (2,), (2, 1)),
#    ('coref', (1,), (2, 1)),
#    ('coref', (3,), (1, 3)),
#    ('coref', (2,), (1, 3)),
#    ('coref', (1,), (1, 3)),
#    ('coref', (3,), (1, 2)),
#    ('coref', (2,), (1, 2)),
#    ('coref', (1,), (1, 2)),
#    ('coref', (3,), (1, 1)),
#    ('coref', (2,), (1, 1)),
#    ('coref', (1,), (1, 1)),
    ('coref', (3,), (3,)),
    ('coref', (3,), (2,)),
    ('coref', (3,), (1,)),
    ('coref', (2,), (3,)),
    ('coref', (2,), (2,)),
    ('coref', (2,), (1,)),
    ('coref', (1,), (3,)),
    ('coref', (1,), (2,)),
    ('coref', (1,), (1,)),
]
POSSIBLE_DROP_ACTIONS = [ # TODO Do we need more? Less?
    ('drop', (3,)),
    ('drop', (2,)),
    ('drop', (1,)),
]
POSSIBLE_LIFT_ACTIONS = [ # TODO Do we need more? Less?
    ('lift', (3,)),
    ('lift', (2,)),
    ('lift', (1,)),
]


class IllegalActionError(Exception):
    pass


def initial(words):
    """Returns the initial item for the given sentence.
    """
    mr = terms.from_string('answer(_, _)')
    stack = lstack.stack((mr,))
    queue = lstack.stack(words)
    finished = False
    return ParseItem(stack, queue, finished, None, None)


class ParseItem:

    def __init__(self, stack, queue, finished, action, pred):
        self.stack = stack
        self.queue = queue
        self.finished = finished
        self.action = action
        self.pred = pred

    def skip(self):
        if not geoquery.skip_allowed(self.queue):
            # HACK: ideally we'd like to allow skipping any word and let the
            # learning algorithm figure out when not to do it. But that makes
            # the search space explode.
            raise IllegalActionError('cannot skip this word')
        stack = self.stack
        queue = self.queue.pop()
        return ParseItem(stack, queue, False, ('skip',), self)

    def shift(self, n, term):
        stack = self.stack.push(term)
        queue = self.queue
        for i in range(n):
            queue = queue.pop()
        return ParseItem(stack, queue, False, ('shift', n, term.to_string()), self)

    def coref(self, address1, address0):
        term1 = self.stack[1].right_address(address1[:-1])
        term0 = self.stack[0].left_address(address0[:-1])
        if not isinstance(term1, terms.ComplexTerm):
            raise IllegalActionError('can only coref arguments of complex terms')
        if not isinstance(term0, terms.ComplexTerm):
            raise IllegalActionError('can only coref arguments of complex terms')
        if not geoquery.coref_allowed(term1, address1[-1]):
            raise IllegalActionError('cannot coref this argument')
        if not geoquery.coref_allowed(term0, address0[-1]):
            raise IllegalActionError('cannot coref this argument')
        old = term1.args[address1[-1] - 1]
        new = term0.args[address0[-1] - 1]
        if not isinstance(old, terms.Variable):
            raise IllegalActionError('can only coref variables')
        if not isinstance(new, terms.Variable):
            raise IllegalActionError('can only coref variables')
        if old == new:
            raise IllegalActionError('variables already corefed')
        stack = lstack.stack(se.replace(old, new) for se in self.stack)
        return ParseItem(stack, self.queue, False, ('coref', address1, address0), self)

    def drop(self, address):
        stack = self.stack
        droppee = stack.head
        stack = stack.pop()
        target_old = stack.head
        stack = stack.pop()
        term = target_old.right_address(address[:-1])
        if not isinstance(term, terms.ComplexTerm):
            raise IllegalActionError('can only drop into arguments of complex terms')
        if not geoquery.integrate_allowed(term, address[-1]):
            raise IllegalActionError('cannot drop into this argument')
        arg_old = term.args[-1]
        if isinstance(arg_old, terms.Variable):
            arg_new = droppee
        elif isinstance(arg_old, terms.ConjunctiveTerm):
            arg_new = terms.ConjunctiveTerm(arg_old.conjuncts + (droppee,))
        else:
            arg_new = terms.ConjunctiveTerm((arg_old, droppee))
        target_new = target_old.replace(arg_old, arg_new)
        stack = stack.push(target_new)
        return ParseItem(stack, self.queue, False, ('drop', address), self)

    def lift(self, address):
        stack = self.stack
        target_old = stack.head
        stack = stack.pop()
        liftee = stack.head
        stack = stack.pop()
        term = target_old.left_address(address[:-1])
        if not isinstance(term, terms.ComplexTerm):
            raise IllegalActionError('can only lift into arguments of complex terms')
        if not geoquery.integrate_allowed(term, address[-1]):
            raise IllegalActionError('cannot lift into this argument')
        arg_old = term.args[-1]
        if isinstance(arg_old, terms.Variable):
            arg_new = liftee
        elif isinstance(arg_old, terms.ConjunctiveTerm):
            arg_new = terms.ConjunctiveTerm((liftee,) + arg_old.conjuncts)
        else:
            arg_new = terms.ConjunctiveTerm((liftee, arg_old))
        target_new = target_old.replace(arg_old, arg_new)
        stack = stack.push(target_new)
        return ParseItem(stack, self.queue, False, ('lift', address), self)

    def finish(self):
        if self.finished:
            raise IllegalActionError('already finished')
        if len(self.stack) != 1:
            raise IllegalActionError('stack size must be 1 to finish')
        if not self.queue.is_empty():
            raise IllegalActionError('queue must be empty to finish')
        return ParseItem(self.stack, self.queue, True, ('finish',), self)

    def idle(self):
        if not self.finished:
            raise IllegalActionError('not finished')
        return ParseItem(self.stack, self.queue, True, ('idle',), self)

    def successors(self):
        """Returns all possible successors.
        """
        # skip
        try:
            yield self.skip()
        except (IndexError, IllegalActionError):
            pass
        # shift
        for token_length in range(1, MAX_TOKEN_LENGTH + 1):
            try:
                token = tuple(self.queue[i] for i in range(token_length))
            except IndexError: # queue too short
                break
            for meaning in lexicon.meanings(token):
                yield self.shift(token_length, meaning)
        # coref
        for _, address1, address0 in POSSIBLE_COREF_ACTIONS:
            try:
                yield self.coref(address1, address0)
            except (IndexError, IllegalActionError):
                continue
        # drop
        for _, address in POSSIBLE_DROP_ACTIONS:
            try:
                yield self.drop(address)
            except (IndexError, IllegalActionError):
                continue
        # lift
        for _, address in POSSIBLE_LIFT_ACTIONS:
            try:
                yield self.lift(address)
            except (IndexError, IllegalActionError):
                continue
        # finish
        if not self.finished and len(self.stack) == 1 and self.queue.is_empty():
            yield self.finish()
        # idle
        if self.finished:
            yield self.idle()

    def action_sequence(self):
        result = []
        item = self
        while item.action is not None:
            result.insert(0, item.action)
            item = item.pred
        return result

    def item_sequence(self):
        result = []
        item = self
        while item is not None:
            result.insert(0, item)
            item = item.pred
        return result

    def __str__(self):
        stack = []
        var_name_dict = terms.make_var_name_dict()
        for term in reversed(self.stack):
            stack.append(term.to_string(var_name_dict))
        return 'ParseItem([' + ', '.join(stack) + '], [' + \
            ', '.join(self.queue) + '], ' + str(self.finished) + ', ' + \
            str(self.action) + ')'
