import collections
import config
import geoquery
import lstack
import oracle
import parsestacks
import terms
import util


INIT_STACK = lstack.stack((parsestacks.new_element(terms.from_string('answer(_,_)')),))


def initial(words):
    """Returns the initial item for the given sentence.
    """
    return ParseItem(INIT_STACK, tuple(words), 0, False, None, None)


class ParseItem:

    def __init__(self, stack, words, offset, finished, action, pred):
        self.stack = stack
        self.words = words
        self.offset = offset
        self.finished = finished
        self.action = action
        self.pred = pred
        self._features = None

    def idle(self):
        if not self.finished:
            raise parsestacks.IllegalAction('not finished')
        return ParseItem(self.stack, self.words, self.offset, True, ('idle',), self)

    def finish(self):
        if self.finished:
            raise parsestacks.IllegalAction('already finished')
        if len(self.stack) != 1:
            raise parsestacks.IllegalAction('stack size must be 1 to finish')
        if not self.stack.head.secstack.is_empty():
            raise parsestacks.IllegalAction('secondary stack must be empty to finish')
        if not self.offset == len(self.words):
            raise parsestacks.IllegalAction('queue must be empty to finish')
        return ParseItem(self.stack, self.words, self.offset, True, ('finish',), self)

    def lift(self, arg_num):
        stack = self.stack
        se_old = stack.head
        stack = stack.pop()
        liftee = stack.head
        stack = stack.pop()
        se_new = se_old.lift(0, arg_num, liftee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.words, self.offset, False, ('lift', arg_num), self)

    def slift(self):
        stack = self.stack
        se_old = stack.head
        stack = stack.pop()
        sliftee = stack.head
        stack = stack.pop()
        se_new = se_old.slift(sliftee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.words, self.offset, False, ('slift',), self)

    def drop(self, arg_num):
        stack = self.stack
        droppee = stack.head
        stack = stack.pop()
        se_old = stack.head
        stack = stack.pop()
        se_new = se_old.drop(0, arg_num, droppee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.words, self.offset, False, ('drop', arg_num), self)

    def sdrop(self):
        stack = self.stack
        sdroppee = stack.head
        stack = stack.pop()
        se_old = stack.head
        stack = stack.pop()
        se_new = se_old.sdrop(sdroppee)
        stack = stack.push(se_new)
        return ParseItem(stack, self.words, self.offset, False, ('sdrop',), self)

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
        return ParseItem(stack, self.words, self.offset, False, ('pop',), self)

    def coref(self, ssp1, arg1, ssp0, arg0):
        se0 = self.stack[0]
        se1 = self.stack[1]
        old, new = se0.coref(ssp0, arg0, se1, ssp1, arg1)
        stack = lstack.stack(parsestacks.StackElement(se.mr.replace(old, new), se.secstack) for se in self.stack)
        return ParseItem(stack, self.words, self.offset, False, ('coref', ssp1, arg1, ssp0, arg0), self)

    def shift(self, n, term):
        se = parsestacks.new_element(term)
        stack = self.stack.push(se)
        if self.offset + n > len(self.words):
            raise IndexError('less than {} words left in queue'.format(n))
        return ParseItem(stack, self.words, self.offset + n, False, ('shift', n, term.to_string()), self)

    def skip(self, lex):
        stack = self.stack
        if self.offset + 1 > len(self.words):
            raise IndexError('no word left in queue')
        return ParseItem(stack, self.words, self.offset + 1, False, ('skip',), self)

    def successor(self, action, lex):
        if action[0] == 'idle':
            return self.idle()
        if action[0] == 'finish':
            return self.finish()
        if action[0] == 'lift':
            return self.lift(action[1])
        if action[0] == 'slift':
            return self.slift()
        if action[0] == 'drop':
            return self.drop(action[1])
        if action[0] == 'sdrop':
            return self.sdrop()
        if action[0] == 'pop':
            return self.pop()
        if action[0] == 'coref':
            return self.coref(action[1], action[2], action[3], action[4])
        if action[0] == 'shift':
            return self.shift(action[1], terms.from_string(action[2]))
        if action[0] == 'skip':
            return self.skip(lex)
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
        except parsestacks.IllegalAction:
            pass
        # lift
        for arg in range(1, 4):
            try:
                yield self.lift(arg)
            except (IndexError, parsestacks.IllegalAction):
                continue
        # slift
        try:
            yield self.slift()
        except (IndexError, parsestacks.IllegalAction):
            pass
        # drop
        for arg in range(1, 4):
            try:
                yield self.drop(arg)
            except (IndexError, parsestacks.IllegalAction):
                continue
        # sdrop
        try:
            yield self.sdrop()
        except (IndexError, parsestacks.IllegalAction):
            pass
        # pop
        try:
            yield self.pop()
        except (IndexError, parsestacks.IllegalAction):
            pass
        # coref
        for ssp1 in range(0, 3):
            for arg1 in range(1, 4):
                for ssp0 in range(0, 2):
                    for arg0 in range(1, 4):
                        try:
                            yield self.coref(ssp1, arg1, ssp0, arg0)
                        except (IndexError, parsestacks.IllegalAction):
                            continue
        # shift
        for token_length in range(1, min(config.MAX_TOKEN_LENGTH,
                                         len(self.words) - self.offset) \
                                     + 1):
            word = self.words[self.offset:self.offset + token_length]
            for meaning in lex.meanings(word):
                yield self.shift(token_length, meaning)
        # skip
        try:
            yield self.skip(lex)
        except (IndexError, parsestacks.IllegalAction):
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
            marked_terms = tuple(se.mr.at_address(a) for a in se.secstack)
            stack.append(se.mr.to_string(var_name_dict, marked_terms))
        return 'ParseItem([' + ', '.join(stack) + '], [' + \
            ', '.join(self.words[self.offset:]) + '], ' + str(self.finished) + ', ' + \
            str(self.action) + ')'

    def local_features(self):
        # The 'bias' feature is present in every item:
        yield 'bias'
        # All other features are template features. We create a dict called
        # tf, mapping templates to the values of these templates for this item.
        tf = {}
        # We first extract the atomic values from the context that we will use
        # in template features.
        def get_stack_predicates():
            for sp, ssp in ((0, 0), (0, 1), (1, 0), (1, 1), (1, 2)):
                try:
                    se = self.stack[sp]
                    yield se.mr.at_address(se.secstack[ssp])
                except IndexError:
                    yield None
        def get_unigrams():
            for i in (-4, -3, -2, -1, 0, 1, 2, 3):
                try:
                    yield self.words[self.offset + i]
                except IndexError:
                    yield None
        def get_last_actions():
            item = self
            for i in range(1):
                yield item.action
                if item.pred is not None:
                    item = item.pred
        s00p, s01p, s10p, s11p, s12p = get_stack_predicates()
        W4, W3, W2, W1, w0, w1, w2, w3 = get_unigrams()
        (a1,) = get_last_actions()
        # Now we populate tf with the template features.
        # Stack predicates
        tf['s00p'] = s00p
        tf['s01p'] = s01p
        tf['s10p'] = s10p
        tf['s11p'] = s11p
        tf['s12p'] = s12p
        # Combinations thereof
        for s0ip in ('s00p', 's01p'):
            for s1jp in ('s10p', 's11p', 's12p'):
                tf[(s0ip, s1jp)] = (tf[s0ip], tf[s1jp])
        # Unigrams
        tf['W4'] = W4
        tf['W3'] = W3
        tf['W2'] = W2
        tf['W1'] = W1
        tf['w0'] = w0
        tf['w1'] = w1
        tf['w2'] = w2
        tf['w3'] = w3
        # Bigrams
        for wi, wj in util.ngrams(2, ('W4', 'W3', 'W2', 'W1', 'w0', 'w1', 'w2', 'w3')):
            tf[(wi, wj)] = (tf[wi], tf[wj])
        # Trigrams
        for wi, wj, wk in util.ngrams(3, ('W4', 'W3', 'W2', 'W1', 'w0', 'w1', 'w2', 'w3')):
            tf[(wi, wj, wk)] = (tf[wi], tf[wj], tf[wk])
        # Previous action
        tf['a1'] = a1
        # Yield all features as strings:
        for template, value in tf.items():
            if isinstance(template, tuple):
                template = ' '.join(template)
            if isinstance(value, tuple):
                value = ' '.join(str(x) for x in value)
            yield template + ' = ' + str(value)

    def features(self):
        if self._features is None:
            if self.pred is None:
                self._features = collections.Counter()
            else:
                self._features = collections.Counter(self.pred.features())
                for f in self.pred.local_features():
                    f = f + ' : ' + str(self.action)
                    self._features[f] += 1
        return self._features
