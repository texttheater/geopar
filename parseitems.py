import collections
import config
import feature_vectors as fv
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

    def local_feature_vector(self):
        """Returns the local feature vector for this item.

        The feature vector is represented as a numpy array with one component
        for every feature template (+ one bias component). The values are
        hashes of the value for each template.
        """
        if self._local_feature_vector is not None:
            return self.local_feature_vector
        vec = fv.LocalFeatureVector()
        # We first extract the atomic values from the context that we will use
        # in template features.
        def get_stack_terms():
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
            for i in range(4):
                yield item.action
                if item.pred is not None:
                    item = item.pred
        def term2functor_name(term):
            if isinstance(term, terms.ConjunctiveTerm):
                term = term.conjuncts[0]
            if term is None:
                return None
            return term.functor_name
        s00, s01, s10, s11, s12 = get_stack_terms()
        W4, W3, W2, W1, w0, w1, w2, w3 = get_unigrams()
        a1, a2, a3, a4 = get_last_actions()
        # Now we populate vec with the template features.
        # Stack predicates
        vec.add(term2functor_name(s00))
        vec.add(term2functor_name(s01))
        vec.add(term2functor_name(s10))
        vec.add(term2functor_name(s11))
        vec.add(term2functor_name(s12))
        # Combinations thereof
        for s0ip in (s00p, s01p):
            for s1jp in (s10p, s11p, s12p):
                vec.add(term2functor_name(s0ip), term2functor_name(s1jp))
        # Stack predicates classes
        vec.add(geoquery.pred_class(s00p))
        vec.add(geoquery.pred_class(s01p))
        vec.add(geoquery.pred_class(s10p))
        vec.add(geoquery.pred_class(s11p))
        vec.add(geoquery.pred_class(s12p))
        # Combinations thereof
        for s0ic in (s00c, s01c):
            for s1jc in (s10c, s11c, s12c):
                vec.add(geoquery.pred_class(s01c), geoquery.pred_class(s1jc))
        # Unigrams
        vec.add(W4)
        vec.add(W3)
        vec.add(W2)
        vec.add(W1)
        vec.add(w0)
        vec.add(w1)
        vec.add(w2)
        vec.add(w3)
        # Bigrams
        for wi, wj in util.ngrams(2, (W4, W3, W2, W1, w0, w1, w2, w3)):
            vec.add(wi, wj)
        # Trigrams
        for wi, wj, wk in util.ngrams(3, (W4, W3, W2, W1, w0, w1, w2, w3)):
            vec.add(wi, wj, wk)
        self._local_feature_vector = vec
        return vec

    def feature_vector(self):
        """Returns the feature vector for this item.

        The feature vector is returned as a numpy array representing a hash
        kernel with a fixed number of dimensions. The values are occurrence
        counts for each bucket across the history of this item.
        """
        if self._feature_vector is not None:
            return self._feature_vector
        if self.pred is None:
            self._features = fv.zeroes()
        else:
            self._features = self.pred.feature_vector() \
                + self.pred.local_feature_vector().with_action(*self.action)
        self._feature_vector = vec
        return vec
