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

    def replace(self, old, new):
        """Replaces the variable old with new.

        Returns a new StackElement where this replacement has been done,
        retaining the secondary stack.
        """
        return StackElement(self.term.replace(old, new), self.secstack)

    def arg(self, secstack_position, arg_num):
        """Returns the i-th argument of the subterm at the given address.

        See terms.ComplexTerm.arg for details.
        """
        if secstack_position == 0:
            address = []
        else:
            address = self.secstack[secstack_position - 1]
        return self.term.arg(address, arg_num)

    def integrate(self, secstack_position, arg_num, subterm):
        """Integrates term into the i-th argument of the term at address.

        See terms.ComplexTerm.integrate for details.
        """
        if secstack_position == 0:
            address = []
        else:
            address = self.secstack[secstack_position - 1]
        term, address = self.term.integrate(address, arg_num, subterm)
        secstack = self.secstack.push(address)
        return StackElement(term, secstack)
