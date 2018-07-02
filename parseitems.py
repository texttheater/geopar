import geoquery
import lexicon
import lstack
import oracle
import parsestacks
import terms


MAX_TOKEN_LENGTH = 3
INIT_STACK = lstack.stack((parsestacks.new_element(terms.from_string('answer(_,_)')),))


def initial(words):
    """Returns the initial item for the given sentence.
    """
    return ParseItem(INIT_STACK, lstack.stack(words), False, None, None)


class ParseItem:

    def __init__(self, stack, queue, finished, action, pred):
        self.stack = stack
        self.queue = queue
        self.finished = finished
        self.action = action
        self.pred = pred

    def coref(self, arg1, arg0):
        stack = self.stack
        se0_old = stack.head
        stack = stack.pop()
        se1 = stack.head
        se0_new = se0_old.coref(arg0, se1, arg1)
        stack = stack.push(se0_new)
        return ParseItem(stack, self.queue, False, ('coref', arg1, arg0), self)

    def lift(self, arg_num):
        stack = self.stack
        se_old = stack.head
        stack = stack.pop()
        liftee = stack.head
        stack = stack.pop()
        se_new = se_old.lift(liftee, arg_num)
        stack = stack.push(se_new)
        return ParseItem(stack, self.queue, False, ('lift', arg_num), self)

    def drop(self, arg_num):
        stack = self.stack
        droppee = stack.head
        stack = stack.pop()
        se_old = stack.head
        stack = stack.pop()
        se_new = se_old.drop(droppee, arg_num)
        stack = stack.push(se_new)
        return ParseItem(stack, self.queue, False, ('drop', arg_num), self)

    def shift(self, n, term):
        se = parsestacks.new_element(term)
        stack = self.stack.push(se)
        queue = self.queue
        for i in range(n):
            queue = queue.pop()
        return ParseItem(stack, queue, False, ('shift', n, term.to_string()), self)

    def skip(self):
        if not geoquery.skip_allowed(self.queue):
            # HACK: ideally we'd like to allow skipping any word and let the
            # learning algorithm figure out when not to do it. But that makes
            # the search space explode.
            raise parsestacks.IllegalAction('cannot skip this word')
        stack = self.stack
        queue = self.queue.pop()
        return ParseItem(stack, queue, False, ('skip',), self)

    def pop(self):
        # pop the topmost element of the secondary stack of the topmost stack
        # element where the secondary stack is nonempty
        stack = self.stack
        tmp = lstack.stack()
        while True:
            if stack.is_empty():
                raise parsestacks.IllegalAction('all secondary stacks are empty')
            if stack.head.secstack.is_empty():
                tmp = tmp.push(stack.head)
                stack = stack.pop()
            else:
                break
        se_old = stack.head
        stack = stack.pop()
        se_new = se_old.pop()
        stack = stack.push(se_new)
        while not tmp.is_empty():
            stack = stack.push(tmp.head)
            tmp = tmp.pop()
        return ParseItem(stack, self.queue, False, ('pop',), self)

    def finish(self):
        if self.finished:
            raise parsestacks.IllegalAction('already finished')
        if len(self.stack) != 1:
            raise parsestacks.IllegalAction('stack size must be 1 to finish')
        if not self.stack.head.secstack.is_empty():
            raise parsestacks.IllegalAction('secondary stack must be empty to finish')
        if not self.queue.is_empty():
            raise parsestacks.IllegalAction('queue must be empty to finish')
        return ParseItem(self.stack, self.queue, True, ('finish',), self)

    def idle(self):
        if not self.finished:
            raise parsestacks.IllegalAction('not finished')
        return ParseItem(self.stack, self.queue, True, ('idle',), self)

    def successor(self, action):
        if action[0] == 'coref':
            return self.coref(action[1], action[2])
        if action[0] == 'lift':
            return self.lift(action[1])
        if action[0] == 'drop':
            return self.drop(action[1])
        if action[0] == 'shift':
            return self.shift(action[1], terms.from_string(action[2]))
        if action[0] == 'skip':
            return self.skip()
        if action[0] == 'pop':
            return self.pop()
        if action[0] == 'finish':
            return self.finish()
        if action[0] == 'idle':
            return self.idle()
        raise ValueError('unknown action type: ' + action[0])

    def successors(self):
        """Returns all possible successors.
        """
        # coref
        for arg1 in range(1, 4):
            for arg0 in range(1, 4):
                try:
                    yield self.coref(arg1, arg0)
                except (IndexError, parsestacks.IllegalAction):
                    continue
        # lift
        for arg in range(1, 4):
            try:
                yield self.lift(arg)
            except (IndexError, parsestacks.IllegalAction):
                continue
        # drop
        for arg in range(1, 4):
            try:
                yield self.drop(arg)
            except (IndexError, parsestacks.IllegalAction):
                continue
        # shift
        for token_length in range(1, MAX_TOKEN_LENGTH + 1):
            try:
                token = tuple(self.queue[i] for i in range(token_length))
            except IndexError: # queue too short
                break
            for meaning in lexicon.meanings(token):
                yield self.shift(token_length, meaning)
        # skip
        try:
            yield self.skip()
        except (IndexError, parsestacks.IllegalAction):
            pass
        # pop
        try:
            yield self.pop()
        except (IndexError, parsestacks.IllegalAction):
            pass
        # finish
        try:
            yield self.finish()
        except parsestacks.IllegalAction:
            pass
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
        for se in reversed(self.stack):
            stack.append(se.mr.to_string(var_name_dict, se.secstack))
        return 'ParseItem([' + ', '.join(stack) + '], [' + \
            ', '.join(self.queue) + '], ' + str(self.finished) + ', ' + \
            str(self.action) + ')'

    def equivalent(self, other):
        if not self.queue == other.queue:
            return False
        if not self.finished == other.finished:
            return False
        if not len(self.stack) == len(other.stack):
            return False
        bindings1 = {}
        bindings2 = {}
        for a, b in zip(self.stack, other.stack):
            if not a.subsumes(b, bindings1):
                return False
            if not b.subsumes(a, bindings2):
                return False
        return True
