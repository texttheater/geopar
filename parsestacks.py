import geoquery
import lstack
import terms


class IllegalAction(Exception):
    pass


def new_element(mr):
    return StackElement(mr, lstack.stack())


class StackElement:

    def __init__(self, mr, secstack):
        self.mr = mr
        self.secstack = secstack

    def _target(self):
        if self.secstack.is_empty():
            return self.mr
        else:
            return self.secstack.head

    def drop(self, other, arg_num):
        if not other.secstack.is_empty():
            raise IllegalAction('cannot drop a stack element with a non-empty secondary stack')
        target = self._target()
        if not isinstance(target, terms.ComplexTerm):
            raise IllegalAction('can only drop into complex terms')
        if not geoquery.integrate_allowed(target, arg_num):
            raise IllegalAction('cannot drop into this argument')
        if len(target.args) < arg_num:
            raise IllegalAction('no such argument')
        old = target.args[arg_num - 1]
        if isinstance(old, terms.Variable):
            new = other.mr
        elif isinstance(old, terms.ConjunctiveTerm):
            new = terms.ConjunctiveTerm(old.conjuncts + (other.mr,))
        else:
            new = terms.ConjunctiveTerm((old, other.mr))
        mr = self.mr.replace(old, new)
        secstack = lstack.stack(m.replace(old, new) for m in self.secstack).push(other.mr)
        return StackElement(mr, secstack)

    def lift(self, other, arg_num):
        if not other.secstack.is_empty():
            raise IllegalAction('cannot lift a stack element with a non-empty secondary stack')
        target = self._target()
        if not isinstance(target, terms.ComplexTerm):
            raise IllegalAction('can only lift into complex terms')
        if not geoquery.integrate_allowed(target, arg_num):
            raise IllegalAction('cannot lift into this argument')
        if len(target.args) < arg_num:
            raise IllegalAction('no such argument')
        old = target.args[arg_num - 1]
        if isinstance(old, terms.Variable):
            new = other.mr
        elif isinstance(old, terms.ConjunctiveTerm):
            new = terms.ConjunctiveTerm((other.mr,) + old.conjuncts)
        else:
            new = terms.ConjunctiveTerm((other.mr, old))
        mr = self.mr.replace(old, new)
        secstack = lstack.stack(m.replace(old, new) for m in self.secstack).push(other.mr)
        return StackElement(mr, secstack)

    def coref(self, arg_num, other, other_arg_num):
        # coref is between the targets of the two topmost elements
        # only the topmost element changes (is this enough??)
        target = self._target()
        if not isinstance(target, terms.ComplexTerm):
            raise IllegalAction('can only coref into complex terms')
        if not geoquery.coref_allowed(target, arg_num):
            raise IllegalAction('cannot coref with this argument')
        if len(target.args) < arg_num:
            raise IllegalAction('no such argument')
        other_target = other._target()
        if not isinstance(other_target, terms.ComplexTerm):
            raise IllegalAction('can only coref into complex terms')
        if not geoquery.coref_allowed(other_target, other_arg_num):
            raise IllegalAction('cannot coref with this argument')
        if len(other_target.args) < other_arg_num:
            raise IllegalAction('no such argument')
        old = target.args[arg_num - 1]
        if not isinstance(old, terms.Variable):
            raise IllegalAction('can only coref variables')
        new = other_target.args[other_arg_num - 1]
        if not isinstance(new, terms.Variable):
            raise IllegalAction('can only coref variables')
        if old == new:
            raise IllegalAction('variables already corefed')
        mr = self.mr.replace(old, new)
        secstack = lstack.stack(m.replace(old, new) for m in self.secstack)
        return StackElement(mr, secstack)

    def pop(self):
        try:
            return StackElement(self.mr, self.secstack.pop())
        except IndexError:
            raise IllegalAction('cannot pop, secondary stack empty')
