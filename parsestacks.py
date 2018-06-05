import lstack
import terms


class IllegalActionError(Exception):
    pass


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
        """Replaces the variable old with new.

        Returns a new StackElement where this replacement has been done,
        retaining the secondary stack.
        """
        if not isinstance(old, terms.Variable):
            raise IllegalActionError('only variables may be replaced')
        if old == new:
            raise IllegalActionError('already the same variable')
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
        """Integrates subterm into the i-th argument of a complex term.

        "Integrating" is what happens with terms that are "dropped" or "lifted"
        into a complex term. If secstack_position is 0, then subterm is
        integrated into the i-th argument of the complex term in this stack
        element. If secstack_position is 1 or higher, subterm is instead
        integrated into the i-th argument of a previously integrated term that
        lives on the secondary stack. subterm becomes the new head of the
        secondary stack.

        This method is non-destructive. It returns a new stack element.
        """
        if not isinstance(subterm, terms.ComplexTerm):
            raise IllegalActionError('only complex terms may be integrated')
        if secstack_position > len(self.secstack):
            raise IllegalActionError('nonexistent secondary stack position')
        if secstack_position == 0:
            address = []
        else:
            address = self.secstack[secstack_position - 1]
        old = self.term.arg(address, arg_num)
        if isinstance(old, terms.Variable):
            new = subterm
            subterm_address = address + [(arg_num, 1)]
        elif isinstance(old, terms.ConjunctiveTerm):
            new = terms.ConjunctiveTerm(old.conjuncts + (subterm,))
            subterm_address = address + [(arg_num, len(new.conjuncts))]
        else:
            new = terms.ConjunctiveTerm((old, subterm))
            subterm_address = address + [(arg_num, 2)]
        return StackElement(self.term.replace(old, new), self.secstack.push(subterm_address)) # TODO replace old everywhere on the stack?
