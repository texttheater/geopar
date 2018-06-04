import lexicon
import lstack
import parsestacks
import terms


MAX_TOKEN_LENGTH = 3
MAX_SECSTACK_DEPTH = 1
MAX_ARGS = 3


def initial(words):
    """Returns the initial item for the given sentence.
    """
    mr = terms.from_string('answer(_, _)')
    se = parsestacks.StackElement(mr)
    stack = lstack.stack((se,))
    queue = lstack.stack(words)
    finished = False
    return ParseItem(stack, queue, finished)


class ParseItem:

    def __init__(self, stack, queue, finished):
        self.stack = stack
        self.queue = queue
        self.finished = finished

    def skip(self):
        stack = self.stack
        queue = self.queue.pop()
        return ParseItem(stack, queue, False)

    def shift(self, n, term):
        se = parsestacks.StackElement(term)
        stack = self.stack.push(se)
        queue = self.queue
        for i in range(n):
            queue = queue.pop()
        return ParseItem(stack, queue, False)

    def coref(self, i, j, k, l):
        old = self.stack[1].arg(i, j)
        new = self.stack[0].arg(k, l)
        stack = lstack.stack(se.replace(old, new) for se in self.stack)
        return ParseItem(stack, self.queue, False)

    def drop(self, i, j):
        stack = self.stack
        droppee = stack.head.term
        stack = stack.pop()
        se_old = stack.head
        stack = stack.pop()
        se_new = se_old.integrate(i, j, droppee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.queue, False)

    def lift(self, i, j):
        stack = self.stack
        se_old = stack.head
        stack = stack.pop()
        liftee = stack.head.term
        stack = stack.pop()
        se_new = se_old.integrate(i, j, liftee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.queue, False)

    def finish(self):
        assert not self.finished
        assert len(self.stack) == 1
        assert self.queue.is_empty()
        return ParseItem(self.stack, self.queue, True)

    def idle(self):
        assert self.finished
        return self

    def successors(self):
        """Returns all possible successors.

        More exactly, returns a dictionary whose keys are the possible actions
        on this item and the values are the resulting successor items.

        Subject to hard-coded maximum arguments for shift, coref, drop, lift
        actions.
        """
        return dict(self._successors())

    def _successors(self):
        # skip
        if not self.queue.is_empty():
            action = ('skip',)
            succ = self.skip()
            yield action, succ
        # shift
        for token_length in range(1, MAX_TOKEN_LENGTH):
            try:
                token = tuple(self.queue[i] for i in range(token_length))
            except IndexError: # queue too short
                break
            for meaning in lexicon.meanings(token):
                action = ('shift', token_length, meaning.to_string())
                succ = self.shift(token_length, meaning)
                yield action, succ
        # coref
        for i in range(MAX_SECSTACK_DEPTH + 1):
            for j in range(1, MAX_ARGS + 1):
                for k in range(MAX_SECSTACK_DEPTH + 1):
                    for l in range(1, MAX_ARGS + 1):
                        action = ('coref', i, j, k, l)
                        try:
                            succ = self.coref(i, j, k, l)
                        except IndexError:
                            continue
                        yield action, succ
        # drop
        for i in range(MAX_SECSTACK_DEPTH + 1):
            for j in range(1, MAX_ARGS + 1):
                action = ('drop', i, j)
                try:
                    succ = self.drop(i, j)
                except IndexError:
                    continue
                yield action, succ
        # lift
        for i in range(MAX_SECSTACK_DEPTH + 1):
            for j in range(1, MAX_ARGS + 1):
                action = ('lift', i, j)
                try:
                    succ = self.lift(i, j)
                except IndexError:
                    continue
                yield action, succ
        # finish
        if not self.finished and len(self.stack) == 1 and self.queue.is_empty():
            action = ('finish',)
            succ = self.finish()
            yield action, succ
        # idle
        if self.finished:
            action = ('idle',)
            succ = self.idle()
            yield action, succ

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
