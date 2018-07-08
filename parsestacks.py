import geoquery
import lstack
import terms


class IllegalAction(Exception):
    pass


def new_element(mr):
    return StackElement(mr, lstack.stack())


def fix_address(address, liftee_address):
    pl = len(liftee_address) - 1
    if address[:pl] == liftee_address[:pl]:
        address = address[:pl] + (address[pl] + 1,) + address[pl + 1:]
    return address


class StackElement:

    def __init__(self, mr, secstack):
        self.mr = mr
        self.secstack = secstack

    def _target_address(self, secstack_position):
        # Retrieve the address at the given position on the secstack.
        # Return () if position == len(self.secstack)
        secstack = self.secstack
        while secstack_position > 0:
            secstack = secstack.tail
            secstack_position -= 1
        if secstack.is_empty():
            address = ()
        else:
            address = secstack.head
        target = self.mr.at_address(address)
        return target, address

    def drop(self, secstack_position, arg_num, other):
        if not other.secstack.is_empty():
            raise IllegalAction('cannot drop a stack element with a non-empty secondary stack')
        target, address_target = self._target_address(secstack_position)
        if not isinstance(target, terms.ComplexTerm):
            raise IllegalAction('can only drop into complex terms')
        if not geoquery.integrate_allowed(target, arg_num):
            raise IllegalAction('cannot drop into this argument')
        if len(target.args) < arg_num:
            raise IllegalAction('no such argument')
        old = target.args[arg_num - 1]
        if isinstance(old, terms.Variable):
            new = other.mr
            conj_num = 1
        elif isinstance(old, terms.ConjunctiveTerm):
            new = terms.ConjunctiveTerm(old.conjuncts + (other.mr,))
            conj_num = len(new.conjuncts)
        else:
            new = terms.ConjunctiveTerm((old, other.mr))
            conj_num = 2
        mr = self.mr.replace(old, new)
        address_droppee = address_target + (arg_num, conj_num)
        secstack = self.secstack.push(address_droppee)
        return StackElement(mr, secstack)

    def lift(self, secstack_position, arg_num, other):
        if not other.secstack.is_empty():
            raise IllegalAction('cannot lift a stack element with a non-empty secondary stack')
        target, address_target = self._target_address(secstack_position)
        if not isinstance(target, terms.ComplexTerm):
            raise IllegalAction('can only lift into complex terms')
        if not geoquery.integrate_allowed(target, arg_num):
            raise IllegalAction('cannot lift into this argument')
        if len(target.args) < arg_num:
            raise IllegalAction('no such argument')
        old = target.args[arg_num - 1]
        if isinstance(old, terms.Variable):
            new = other.mr
            conj_num = 1
        elif isinstance(old, terms.ConjunctiveTerm):
            new = terms.ConjunctiveTerm((other.mr,) + old.conjuncts)
            conj_num = 1
        else:
            new = terms.ConjunctiveTerm((other.mr, old))
            conj_num = 1
        mr = self.mr.replace(old, new)
        address_liftee = address_target + (arg_num, conj_num)
        secstack = lstack.stack(fix_address(a, address_liftee) for a in self.secstack).push(address_liftee)
        return StackElement(mr, secstack)

    def coref(self, arg_num, other, other_arg_num):
        # coref is between the targets of the two topmost elements
        # only the topmost element changes (is this enough??)
        target, _ = self._target_address(0)
        if not isinstance(target, terms.ComplexTerm):
            raise IllegalAction('can only coref into complex terms')
        if not geoquery.coref_allowed(target, arg_num):
            raise IllegalAction('cannot coref with this argument')
        if len(target.args) < arg_num:
            raise IllegalAction('no such argument')
        other_target, _ = other._target_address(0)
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
        return old, new

    def pop(self):
        try:
            return StackElement(self.mr, self.secstack.pop())
        except IndexError:
            raise IllegalAction('cannot pop, secondary stack empty')
