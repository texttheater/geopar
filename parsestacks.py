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
        if not isinstance(old, terms.Variable):
            raise IllegalAction('can only drop into variable arguments')
        new = other.mr
        conj_num = 1
        mr = self.mr.replace(old, new)
        secstack = self.secstack
        address_droppee = address_target + (arg_num, conj_num)
        secstack = secstack.push(address_droppee)
        return StackElement(mr, secstack)

    def sdrop(self, other):
        if not other.secstack.is_empty():
            raise IllegalAction('cannot drop a stack element with a non-empty secondary stack')
        if not isinstance(other.mr, terms.ComplexTerm):
            raise IllegalAction('can only sdrop complex terms')
        sibling, sibling_address =  self._target_address(0)
        # Determine the old term to be replaced:
        if len(sibling_address) == 0:
            old = sibling
        elif len(sibling_address) == 1:
            old = self.mr
        else:
            *parent_address, arg_num, conj_num = sibling_address
            parent_address = tuple(parent_address)
            parent = self.mr.at_address(parent_address)
            old = parent.args[arg_num - 1]
        # Determine the new (conjunctive term) to replace it with:
        if isinstance(old, terms.ConjunctiveTerm):
            new = terms.ConjunctiveTerm(old.conjuncts + (other.mr,))
            conj_num = len(new.conjuncts)
        else:
            new = terms.ConjunctiveTerm((old, other.mr))
            conj_num = 2
        mr = self.mr.replace(old, new)
        # Put the new conjunct onto the secondary stack:
        if len(sibling_address) < 2:
            droppee_address = (conj_num,)
        else:
            droppee_address = parent_address + (arg_num, conj_num)
        secstack = self.secstack.push(droppee_address)
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
        if not isinstance(old, terms.Variable):
            raise IllegalAction('can only lift into variable arguments')
        new = other.mr
        conj_num = 1
        mr = self.mr.replace(old, new)
        secstack = self.secstack
        address_liftee = address_target + (arg_num, conj_num)
        secstack = secstack.push(address_liftee)
        return StackElement(mr, secstack)

    def coref(self, secstack_position, arg_num, other, other_secstack_position, other_arg_num):
        # coref is between the targets of the two topmost elements
        target, _ = self._target_address(secstack_position)
        if not isinstance(target, terms.ComplexTerm):
            raise IllegalAction('can only coref into complex terms')
        if not geoquery.coref_allowed(target, arg_num):
            raise IllegalAction('cannot coref with this argument')
        if len(target.args) < arg_num:
            raise IllegalAction('no such argument')
        other_target, _ = other._target_address(other_secstack_position)
        if isinstance(other_target, terms.ConjunctiveTerm):
            other_target = other_target.conjuncts[0]
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
