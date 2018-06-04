import lstack
import parsestacks
import terms


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
        assert not self.finished
        stack = self.stack
        queue = self.queue.pop()
        return ParseItem(stack, queue, False)

    def shift(self, n, term):
        assert not self.finished
        se = parsestacks.StackElement(term)
        stack = self.stack.push(se)
        queue = self.queue
        for i in range(n):
            queue = queue.pop()
        return ParseItem(stack, queue, False)

    def coref(self, i, j, k, l):
        assert not self.finished
        old = self.stack[1].arg(i, j)
        new = self.stack[0].arg(k, l)
        stack = lstack.stack(se.replace(old, new) for se in self.stack)
        return ParseItem(stack, self.queue, False)

    def drop(self, i, j):
        assert not self.finished
        stack = self.stack
        droppee = stack.head.term
        stack = stack.pop()
        se_old = stack.head
        stack = stack.pop()
        se_new = se_old.integrate(i, j, droppee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.queue, False)

    def lift(self, i, j):
        assert not self.finished
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
