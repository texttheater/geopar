import lstack
import terms


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

    def integrate(self, secstack_position, arg_num, subterm):
        if secstack_position == 0:
            address = []
        else:
            address = self.secstack[secstack_position - 1]
        term, address = self.term.integrate(address, arg_num, subterm)
        secstack = self.secstack.push(address)
        return StackElement(term, secstack)

