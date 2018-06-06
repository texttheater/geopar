import geoquery
import lexicon
import lstack
import parsestacks
import terms


MAX_TOKEN_LENGTH = 3
MAX_SECSTACK_DEPTH = 1
MAX_ARGS = 3


class IllegalActionError(Exception):
    pass


def initial(words):
    """Returns the initial item for the given sentence.
    """
    mr = terms.from_string('answer(_, _)')
    se = parsestacks.StackElement(mr)
    stack = lstack.stack((se,))
    queue = lstack.stack(words)
    finished = False
    actions = lstack.stack()
    return ParseItem(stack, queue, finished, actions)


class ParseItem:

    def __init__(self, stack, queue, finished, actions):
        self.stack = stack
        self.queue = queue
        self.finished = finished
        self.actions = actions

    def skip(self):
        if not geoquery.skip_allowed(self.queue):
            # HACK: ideally we'd like to allow skipping any word and let the
            # learning algorithm figure out when not to do it. But that makes
            # the search space explode.
            raise IllegalActionError('cannot skip this word')
        stack = self.stack
        queue = self.queue.pop()
        return ParseItem(stack, queue, False, self.actions.push(('skip',)))

    def shift(self, n, term):
        se = parsestacks.StackElement(term)
        stack = self.stack.push(se)
        queue = self.queue
        for i in range(n):
            queue = queue.pop()
        return ParseItem(stack, queue, False, self.actions.push(('shift', n, term.to_string())))

    def coref(self, i, j, k, l):
        term1 = self.stack[1].at_secstack_position(i)
        term0 = self.stack[0].at_secstack_position(k)
        if not geoquery.coref_allowed(term1, j):
            raise IllegalActionError('cannot coref this argument')
        if not geoquery.coref_allowed(term0, l):
            raise IllegalActionError('cannot coref this argument')
        old = term1.args[j - 1]
        new = term0.args[l - 1]
        if not isinstance(old, terms.Variable):
            raise IllegalActionError('can only coref variables')
        if not isinstance(new, terms.Variable):
            raise IllegalActionError('can only coref variables')
        if old == new:
            raise IllegalActionError('variables already corefed')
        stack = lstack.stack(se.replace(old, new) for se in self.stack)
        return ParseItem(stack, self.queue, False, self.actions.push(('coref', i, j, k, l)))

    def drop(self, i, j):
        stack = self.stack
        droppee = stack.head.term
        stack = stack.pop()
        se_old = stack.head
        stack = stack.pop()
        se_new = se_old.drop(i, j, droppee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.queue, False, self.actions.push(('drop', i, j)))

    def lift(self, i, j):
        stack = self.stack
        se_old = stack.head
        stack = stack.pop()
        liftee = stack.head.term
        stack = stack.pop()
        se_new = se_old.lift(i, j, liftee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.queue, False, self.actions.push(('lift', i, j)))

    def finish(self):
        if self.finished:
            raise IllegalActionError('already finished')
        if len(self.stack) != 1:
            raise IllegalActionError('stack size must be 1 to finish')
        if not self.queue.is_empty():
            raise IllegalActionError('queue must be empty to finish')
        return ParseItem(self.stack, self.queue, True, self.actions.push(('finish',)))

    def idle(self):
        if not self.finished:
            raise IllegalActionError('not finished')
        return ParseItem(self.stack, self.queue, True, self.actions.push(('idle',)))

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
        for i in range(MAX_SECSTACK_DEPTH, -1, -1):
            for j in range(1, MAX_ARGS + 1):
                for k in range(MAX_SECSTACK_DEPTH, -1, -1):
                    for l in range(1, MAX_ARGS + 1):
                        try:
                            yield self.coref(i, j, k, l)
                        except (IndexError, IllegalActionError):
                            continue
        # drop
        for i in range(MAX_SECSTACK_DEPTH, -1, -1):
            for j in range(1, MAX_ARGS + 1):
                try:
                    yield self.drop(i, j)
                except (IndexError, IllegalActionError):
                    continue
        # lift
        for i in range(MAX_SECSTACK_DEPTH, -1, -1):
            for j in range(1, MAX_ARGS + 1):
                try:
                    yield self.lift(i, j)
                except (IndexError, IllegalActionError):
                    continue
        # finish
        if not self.finished and len(self.stack) == 1 and self.queue.is_empty():
            yield self.finish()
        # idle
        if self.finished:
            yield self.idle()

    def successor(self, action, *args):
        if action == 'skip':
            return self.skip(*args)
        elif action == 'shift':
            length, meaning = args
            meaning = terms.from_string(meaning)
            return self.shift(length, meaning)
        elif action == 'coref':
            return self.coref(*args)
        elif action == 'drop':
            return self.drop(*args)
        elif action == 'lift':
            return self.lift(*args)
        elif action == 'finish':
            return self.finish(*args)
        elif action == 'idle':
            return self.idle(*args)
        else:
            raise ValueError('invalid action: ' + action)

    def action_sequence(self):
        return list(reversed(self.actions))
