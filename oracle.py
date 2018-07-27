import augment
import collections
import config
import data
import itertools
import lexicon
import parseitems
import terms
import util


class Oracle:

    def possible_actions(self, item):
        result = []
        result.extend(self.possible_idle_actions(item))
        if result:
            return result
        result.extend(self.possible_finish_actions(item))
        if result:
            return result
        result.extend(self.possible_reduce_actions(item))
        result.extend(self.possible_merge_actions(item))
        result.extend(self.possible_confirm_actions(item))
        if result:
            if parseitems.is_word(item.stack[0]): # also need to consider shift b/c possible multiwords
                result.extend(self.possible_shift_actions(item))
            return result
        result.extend(self.possible_arc_actions(item))
        if result:
            return result
        result.extend(self.possible_swap_actions(item))
        if result:
            return result
        result.extend(self.possible_shift_actions(item))
        return result


class GeoQueryOracle(Oracle):

    def __init__(self, target_mr, lex):
        target_mr = terms.ComplexTerm('root', (target_mr,))
        self.lex = augment.AugmentingLexicon(lex, target_mr)
        target_mr = target_mr.augment()
        self.root = target_mr
        self.subroot = target_mr.args[0]
        self.nodes, self.edges = terms2graph((target_mr,))

    def possible_idle_actions(self, item):
        if item.finished:
            return [('idle',)]
        return []

    def possible_finish_actions(self, item):
        if not item.finished and item.stack.is_empty() and item.queue.is_empty():
            return [('finish',)]
        return []

    def possible_merge_actions(self, item):
        if item.stack.is_empty():
            return []
        if item.stack.tail.is_empty():
            return []
        if not parseitems.is_word(item.stack[0]):
            return []
        if not parseitems.is_word(item.stack[1]):
            return []
        return [('merge',)]

    def possible_confirm_actions(self, item):
        result = []
        if item.stack.is_empty():
            return result
        if len(item.stack) > 1 and parseitems.is_word(item.stack[1]):
            return result # need to merge first
        established_nodes, _ = self.established_graph(item)
        potential_nodes = queue_nodes(item.queue, self.lex)
        for meaning in self.lex.meanings(item.stack[0]):
            node = meaning.to_string()
            if node in established_nodes:
                continue # already used that node
            if not self.nodes <= established_nodes | set((node,)) | potential_nodes:
                continue # we would be missing a lexical MR that we need
            result.append(('confirm', node))
        return result

    def possible_shift_actions(self, item):
        if item.queue.is_empty():
            return []
        if item.stack.is_empty():
            return [('shift',)]
        if parseitems.is_word(item.stack[0]) and not parseitems.is_word(item.queue[0]):
            return []
        if parseitems.is_word(item.stack[0]) and len(item.stack[0]) >= config.MAX_TOKEN_LENGTH:
            return []
        if item.stack.tail.is_empty():
            return [('shift',)]
        if parseitems.is_word(item.stack[0]) and parseitems.is_word(item.stack[1]):
            return [] # need to merge first
        return [('shift',)]

    def established_graph(self, item):
        established_mrs = []
        established_mrs.extend(se for se in item.stack if parseitems.is_node(se))
        established_mrs.extend(qe for qe in item.queue if parseitems.is_node(qe))
        if item.root is not None:
            established_mrs.append(item.root)
        return terms2graph(established_mrs)

    def possible_reduce_actions(self, item):
        if item.stack.is_empty():
            #print(1)
            return []
        if len(item.stack) >= 2 and parseitems.is_word(item.stack[1]):
            #print(1.5)
            return []
        established_nodes, established_edges = self.established_graph(item)
        if parseitems.is_word(item.stack[0]):
            if len(item.stack[0]) > 1:
                #print(2)
                return [] # only reduce single words
            potential_nodes = queue_nodes(item.queue, self.lex)
            print(self.nodes)
            print(established_nodes)
            print(potential_nodes)
            if not self.nodes <= established_nodes | potential_nodes:
                #print(3)
                return [] # if we reduce this word then we would be missing a lexical MR that we need
        else:
            node = parseitems.term2node(item.stack[0])
            for node2, edges in self.edges[node].items():
                for edge in edges:
                    if not edge in established_edges[node][node2]:
                        #print(4)
                        return [] # stack top doesn't have all required outgoing edges yet
            for node2, e2 in self.edges.items():
                for edge in e2[node]:
                    if not edge in established_edges[node2][node]:
                        #print(5)
                        return [] # stack top doesn't have all required incoming edges yet
        return [('reduce',)]

    def possible_arc_actions(self, item):
        if item.stack.is_empty():
            return []
        if not parseitems.is_node(item.stack[0]):
            return []
        if item.stack.tail.is_empty():
            return []
        if not parseitems.is_node(item.stack[1]):
            return []
        _, established_edges = self.established_graph(item)
        node0 = parseitems.term2node(item.stack[0])
        node1 = parseitems.term2node(item.stack[1])
        for edge in self.edges[node0][node1]:
            if not edge in established_edges[node0][node1]:
                return [('larc', edge)]
        for edge in self.edges[node1][node0]:
            if not edge in established_edges[node1][node0]:
                return [('rarc', edge)]
        return []

    def possible_swap_actions(self, item):
        if len(item.stack) < 2:
            return []
        if item.action is not None and item.action[0] in ('reduce', 'larc', 'rarc', 'confirm', 'swap'):
            return [('swap',)]
        return []
        #if item.action is not None and item.action[0] == 'larc':
        #    return [('swap',)]
        #if item.action is not None and item.action[0] == 'shift':
        #    return []
        #if len(item.stack) < 2:
        #    return []
        #if not parseitems.is_node(item.stack[0]):
        #    return []
        #established_nodes, _ = self.established_graph(item)
        #s0 = parseitems.term2node(item.stack[0])
        ## See if we need an edge between s0 and any not-yet-established node:
        #for node, edges in self.edges[s0].items():
        #    if node not in established_nodes and edges:
        #        return []
        #for node, e2 in self.edges.items():
        #    if node in established_nodes:
        #        continue
        #    if e2[s0]:
        #        return []
        #s1 = parseitems.term2node(item.stack[1])
        ## See if we need an edge between s1 and any not-yet-established node:
        #for node, edges in self.edges[s1].items():
        #    if node not in established_nodes and edges:
        #        return [('swap',)]
        #for node, e2 in self.edges.items():
        #    if node in established_nodes:
        #        continue
        #    if e2[s1]:
        #        return [('swap',)]
        #return []


def find_arg_number(parent_term, child_term):
    for i, arg in enumerate(parent_term.args, start=1):
        if isinstance(arg, terms.ConjunctiveTerm):
            for conj in arg.conjuncts:
                if conj == child_term:
                    return i
        elif arg == child_term:
            return i
    return 0


def find_coref_arg_numbers(term1, term2):
    for i, arg1 in enumerate(term1.args, start=1):
        for j, arg2 in enumerate(term2.args, start=1):
            if arg1 == arg2:
                yield i, j


def nody_subterms(term):
    if isinstance(term, terms.ComplexTerm):
        yield term
        if not (term.functor_name.startswith('const') and len(term.args) == 2):
            for arg in term.args:
                yield from nody_subterms(arg)
    elif isinstance(term, terms.ConjunctiveTerm):
        for conj in term.conjuncts:
            yield from nody_subterms(conj)


def terms2graph(trms):
    subterms = [s for t in trms for s in nody_subterms(t)]
    nodes = [parseitems.term2node(s) for s in subterms]
    # edges is a mapping: parent node -> child node -> set of edge labels
    # for embedding edges, parent = containing term; child = contained term
    # coreference edges are doubly represented, once for each direction
    edges = collections.defaultdict(lambda: collections.defaultdict(set))
    for parent_node, parent_term in zip(nodes, subterms):
        for child_node, child_term in zip(nodes, subterms):
            if parent_node == child_node:
                continue
            arg_number = find_arg_number(parent_term, child_term)
            if arg_number:
                edges[parent_node][child_node].add(('embed', arg_number))
            for arg_number_1, arg_number_2 in find_coref_arg_numbers(parent_term, child_term):
                edges[parent_node][child_node].add(('coref', arg_number_1, arg_number_2))
    nodes = set(nodes)
    return nodes, edges


def queue_nodes(queue, lex):
    result = set()
    for qe in queue:
        if parseitems.is_node(qe):
            result.add(qe.to_string())
    for length in range(1, config.MAX_TOKEN_LENGTH + 1):
        for ngram in util.ngrams(length, list(queue)):
            if all(parseitems.is_word(qe) for qe in ngram):
                word = tuple(itertools.chain(*ngram))
                for meaning in lex.meanings(word):
                    result.add(meaning.to_string())
    return result


def print_beam(beam):
    for item in beam:
        print(item)
    print()


def action_sequence(words, target_mr):
    """Looks for action sequences that lead from words to target_mr.

    Returns the first that it finds.
    """
    lex = lexicon.read_lexicon('lexicon.txt')
    oracle = GeoQueryOracle(target_mr, lex)
    beam = [parseitems.initial(words, terms.from_string(parseitems.term2node(oracle.root)), terms.from_string(parseitems.term2node(oracle.subroot)))]
    print_beam(beam)
    while not all(item.finished for item in beam):
        new_beam = []
        for item in beam:
            actions = oracle.possible_actions(item)
            for action in actions:
                new_beam.append(item.successor(action, lex))
        beam = new_beam
        print_beam(beam)
        for item in beam:
            if item.finished and \
                item.root.unaugment().args[0].equivalent(target_mr):
                return item.action_sequence()
    raise ValueError('no action sequence found')


if __name__ == '__main__':
    for _, mr in data.geo880_train():
        nodes, edges = mr2graph(mr)
        for node in nodes:
            print(node)
        for node1, e2 in edges.items():
            for node2, labels in e2.items():
                for label in labels:
                    print(node1, node2, label)
        print()
