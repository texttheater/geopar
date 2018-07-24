import config
import geoquery
import itertools
import lexicon
import lstack
import oracle
import terms


def initial(words, root, subroot):
    """Returns the initial item for the given sentence.
    """
    return ParseItem(lstack.stack((subroot,)), lstack.stack(itertools.chain(((w,) for w in words), (root,))), None, False, None, None)


def is_word(stack_element):
    return isinstance(stack_element, tuple)


def is_node(stack_element):
    return isinstance(stack_element, terms.ComplexTerm)


def replace(old, new, elements):
    for element in elements:
        if is_node(element):
            yield element.replace(old, new)
        else:
            yield element


class IllegalAction(Exception):
    pass


class ParseItem:

    def __init__(self, stack, queue, root, finished, action, pred):
        self.stack = stack
        self.queue = queue
        self.root = root
        self.finished = finished
        self.action = action
        self.pred = pred

    def idle(self):
        if not self.finished:
            raise IllegalAction('not finished')
        return ParseItem(self.stack, self.queue, self.root, True, ('idle',), self)

    def finish(self):
        if self.finished:
            raise IllegalAction('already finished')
        if not self.stack.is_empty():
            raise IllegalAction('stack must be empty to finish')
        if not self.queue.is_empty():
            raise IllegalAction('queue must be empty to finish')
        return ParseItem(self.stack, self.queue, self.root, True, ('finish',), self)

    def merge(self):
        if len(self.stack) < 2:
            raise IllegalAction('nothing to merge')
        if not is_word(self.stack[0]) or not is_word(self.stack[1]):
            raise IllegalAction('can only merge words')
        stack = self.stack
        w0 = stack.head
        stack = stack.pop()
        w1 = stack.head
        stack = stack.pop()
        w = w1 + w0
        stack = stack.push(w)
        return ParseItem(stack, self.queue, self.root, False, ('merge',), self)

    def confirm(self, meaning):
        if self.stack.is_empty() or not is_word(self.stack[0]):
            raise IllegalAction('nothing to confirm')
        if len(self.stack) > 1 and is_word(self.stack[1]):
            raise IllegalAction('confirm not allowed when s[1] is a word') 
        stack = self.stack
        stack = stack.pop()
        stack = stack.push(meaning)
        return ParseItem(stack, self.queue, self.root, False, ('confirm', meaning.to_string()), self)

    def shift(self):
        if self.queue.is_empty():
            raise IllegalAction('nothing to shift')
        if len(self.stack) >= 2 and is_word(self.stack[0]) and is_word(self.stack[1]):
            raise IllegalAction('already more than 1 word on stack, shift not allowed')
        if len(self.stack) >= 2 and is_word(self.stack[0]) and len(self.stack[0]) >= config.MAX_TOKEN_LENGTH:
            raise IllegalAction('word on stack is too long to shift again')
        if not self.stack.is_empty() and is_word(self.stack[0]) and not is_word(self.queue[0]):
            raise IllegalAction('cannot shift node onto a word')
        stack = self.stack.push(self.queue.head)
        queue = self.queue.pop()
        return ParseItem(stack, queue, self.root, False, ('shift',), self)

    def reduce(self):
        if self.stack.is_empty():
            raise IllegalAction('nothing to reduce')
        if is_word(self.stack[0]) and len(self.stack[0]) > 1:
            raise IllegalAction('can only reduce single words')
        stack = self.stack.pop()
        if is_node(self.stack[0]) and self.stack[0].functor_name.startswith('root'):
            root = self.stack[0]
        else:
            root = self.root
        return ParseItem(stack, self.queue, root, False, ('reduce',), self)

    def larc(self, label):
        if len(self.stack) < 2:
            raise IllegalAction('no nodes to make an arc between')
        if not is_node(self.stack[0]) or not is_node(self.stack[1]):
            raise IllegalAction('can only make arcs between nodes')
        if label[0] == 'coref':
            if not geoquery.coref_allowed(self.stack[0], label[1]):
                raise IllegalAction('cannot coref this argument')
            if not geoquery.coref_allowed(self.stack[1], label[2]):
                raise IllegalAction('cannot coref this argument')
            old = self.stack[0].args[label[1] - 1]
            new = self.stack[1].args[label[2] - 1]
            if not isinstance(old, terms.Variable):
                raise IllegalAction('can only corefer variables')
            if not isinstance(new, terms.Variable):
                raise IllegalAction('can only corefer variables')
            if old == new:
                raise IllegalAction('variables already corefer')
            stack = lstack.stack(replace(old, new, self.stack))
            queue = lstack.stack(replace(old, new, self.queue))
            return ParseItem(stack, queue, self.root, False, ('larc', label), self)
        else:
            assert label[0] == 'embed'
            parent = self.stack[0]
            child = self.stack[1]
            if not geoquery.integrate_allowed(parent, label[1]):
                raise IllegalAction('cannot embed into this argument')
            old = parent.args[label[1] - 1]
            if isinstance(old, terms.Variable):
                new = child
            elif isinstance(old, terms.ConjunctiveTerm):
                new = terms.ConjunctiveTerm((child,) + old.conjuncts)
            else:
                new = terms.ConjunctiveTerm((child, old))
            result = parent.replace(old, new)
            stack = lstack.stack(replace(parent, result, self.stack))
            queue = lstack.stack(replace(parent, result, self.queue))
            return ParseItem(stack, queue, self.root, False, ('larc', label), self)

    def rarc(self, label):
        if len(self.stack) < 2:
            raise IllegalAction('no nodes to make an arc between')
        if not is_node(self.stack[0] or not is_node(self.stack[1])):
            raise IllegalAction('can only make arcs between nodes')
        if label[0] == 'coref':
            if not geoquery.coref_allowed(self.stack[1], label[1]):
                raise IllegalAction('cannot coref this argument')
            if not geoquery.coref_allowed(self.stack[0], label[2]):
                raise IllegalAction('cannot coref this argument')
            old = self.stack[1].args[label[1] - 1]
            new = self.stack[0].args[label[2] - 1]
            if not isinstance(old, terms.Variable):
                raise IllegalAction('can only corefer variables')
            if not isinstance(new, terms.Variable):
                raise IllegalAction('can only corefer variables')
            if old == new:
                raise IllegalAction('variables already corefer')
            stack = lstack.stack(replace(old, new, self.stack))
            queue = lstack.stack(replace(old, new, self.queue))
            return ParseItem(stack, queue, self.root, False, ('rarc', label), self)
        else:
            assert label[0] == 'embed'
            parent = self.stack[1]
            child = self.stack[0]
            if not geoquery.integrate_allowed(parent, label[1]):
                raise IllegalAction('cannot embed into argument ', label[1], ' of ', parent.functor_name)
            old = parent.args[label[1] - 1]
            if isinstance(old, terms.Variable):
                new = child
            elif isinstance(old, terms.ConjunctiveTerm):
                new = terms.ConjunctiveTerm(old.conjuncts + (child,))
            else:
                new = terms.ConjunctiveTerm((old, child))
            result = parent.replace(old, new)
            stack = lstack.stack(replace(parent, result, self.stack))
            queue = lstack.stack(replace(parent, result, self.queue))
            return ParseItem(stack, queue, self.root, False, ('rarc', label), self)

    def swap(self):
        if len(self.stack) < 2:
            raise IllegalAction('nothing to swap')
        if not is_node(self.stack[0]):
            raise IllegalAction('can only swap when stack top is a node')
        stack = self.stack
        s0 = stack.head
        stack = stack.pop()
        s1 = stack.head
        stack = stack.pop()
        queue = self.queue.push(s1)
        stack = stack.push(s0)
        return ParseItem(stack, queue, self.root, False, ('swap',), self)

    def successor(self, action, lex):
        if action[0] == 'idle':
            return self.idle()
        if action[0] == 'finish':
            return self.finish()
        if action[0] == 'merge':
            return self.merge()
        if action[0] == 'confirm':
            return self.confirm(terms.from_string(action[1]))
        if action[0] == 'shift':
            return self.shift()
        if action[0] == 'reduce':
            return self.reduce()
        if action[0] == 'larc':
            return self.larc(action[1])
        if action[0] == 'rarc':
            return self.rarc(action[1])
        if action[0] == 'swap':
            return self.swap()
        raise ValueError('unknown action type: ' + action[0])

    def successors(self, lex):
        """Returns all possible successors.
        """
        # idle
        if self.finished:
            yield self.idle()
        # finish
        try:
            yield self.finish()
        except IllegalAction:
            pass
        # merge
        try:
            yield self.merge()
        except IllegalAction:
            pass
        # confirm
        if not self.stack.is_empty() and is_word(self.stack[0]):
            for meaning in lex.meanings(self.stack[0]):
                try:
                    yield self.confirm(meaning)
                except IllegalAction:
                    break
        # shift
        try:
            yield self.shift()
        except IllegalAction:
            pass
        # reduce
        try:
            yield self.reduce()
        except IllegalAction:
            pass
        # larc
        for i in range(1, 4):
            for j in range(1, 4):
                try:
                    yield self.larc(('coref', i, j))
                except IllegalAction:
                    pass
        for i in range(1, 4):
            try:
                yield self.larc(('embed', i))
            except IllegalAction:
                pass
        # rarc TODO okay to leave coref entirely to larc?
        for i in range(1, 4):
            try:
                yield self.rarc(i)
            except IllegalAction:
                pass
        # swap
        try:
            yield self.swap()
        except IllegalAction:
            pass

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
            if isinstance(se, terms.Term):
                stack.append(se.to_string(var_name_dict))
            else:
                stack.append(repr(se))
        queue = []
        for qe in self.queue:
            if isinstance(qe, terms.Term):
                queue.append(qe.to_string(var_name_dict))
            else:
                queue.append(repr(qe))
        if self.root is None:
            root = 'None'
        else:
            root = self.root.to_string()
        return 'ParseItem([' + ', '.join(stack) + '], [' + \
            ', '.join(queue) + '], ' + root + ', ' + str(self.finished) + ', ' + \
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
