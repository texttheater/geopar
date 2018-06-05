import geoquery
import lstack
import parseitems
import terms


def to_string(stack):
    l = []
    var_name_dict = terms.make_var_name_dict()
    for se in stack:
        l.append((se.term.to_string(var_name_dict),
            list(se.secstack)))
    return str(l)


class StackElement:

    """Represents an element of the stack of an item.

    Contains the term at a particular stack position as well as a "secondary
    stack". The secondary stack is a stack of addresses of the subterms that
    were most recently "dropped" or "lifted" into the term.

    Dropping/lifting should be done by calling the StackElement's integrate
    method, to make sure the secondary stack is kept up to date.
    """

    def __init__(self, term, secstack=None):
        if secstack == None:
            secstack = lstack.stack()
        self.term = term
        self.secstack = secstack

    def replace(self, old, new):
        """Replaces the term old with new.

        Returns a new StackElement where this replacement has been done,
        retaining the secondary stack.
        """
        return StackElement(self.term.replace(old, new), self.secstack)

    def at_secstack_position(self, pos):
        """Returns the term at the given secondary stack position.
        """
        if pos == 0:
            address = []
        else:
            address = self.secstack[pos - 1]
        return self.term.at_address(address)

    def drop(self, pos, arg_num, droppee):
        if pos == 0:
            address = []
        else:
            address = self.secstack[pos - 1]
        old = self.term.at_address(address)
        if not isinstance(old, terms.ComplexTerm):
            raise parseitems.IllegalActionError('can only drop into complex terms')
        if not geoquery.integrate_allowed(old, arg_num):
            raise parseitems.IllegalActionError('cannot drop into this argument')
        new, conj_num = old.drop(arg_num, droppee)
        term = self.term.replace(old, new)
        secstack = self.secstack.push(address + [(arg_num, conj_num)])
        return StackElement(term, secstack)

    def lift(self, pos, arg_num, liftee):
        if pos == 0:
            address = []
        else:
            address = self.secstack[pos - 1]
        old = self.term.at_address(address)
        if not isinstance(old, terms.ComplexTerm):
            raise parseitems.IllegalActionError('can only lift into complex terms')
        if not geoquery.integrate_allowed(old, arg_num):
            raise parseitems.IllegalActionError('cannot lift into this argument')
        new, conj_num = old.lift(arg_num, liftee)
        term = self.term.replace(old, new)
        secstack = self.secstack.push(address + [(arg_num, conj_num)])
        # TODO adapt addresses??
        return StackElement(term, secstack)
