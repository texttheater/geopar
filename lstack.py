"""Provides a linked stack implementation.

Linked stacks are similar to Prolog lists: elements can efficiently be added at
the beginning, and two stacks with the same tail can be structure-shared,
saving memory and copying operations. Useful for implementing the stack and
queue of the parse item.

The "head" of a nonempty linked stack is its first element. Its "tail" is the
linked stack with all the other elements.
"""


def stack(elements=()):
    """Creates a new stack with the elements in the given sequence.
    """
    it = iter(elements)
    try:
        head = next(it)
        tail = stack(it)
        return _NonEmptyLinkedStack(head, tail)
    except StopIteration:
        return _EMPTY_LINKED_STACK


class LinkedStack:

    def push(self, element):
        """Returns a new linked stack with element added at the beginning.
        """
        return _NonEmptyLinkedStack(element, self)

    def __getitem__(self, index):
        if index == 0:
            return self.head
        return self.tail[index - 1]


class _EmptyLinkedStack(LinkedStack):

    def is_empty(self):
        return True

    def pop(self):
        raise IndexError()

    def __len__(self):
        return 0

    @property
    def head(self):
        raise IndexError()

    @property
    def tail(self):
        raise IndexError()

    def __iter__(self):
        # This is how you define an empty generator function:
        return
        yield


_EMPTY_LINKED_STACK = _EmptyLinkedStack()


class _NonEmptyLinkedStack(LinkedStack):

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def is_empty(self):
        return False

    def pop(self):
        """Returns the tail of this linked stack."""
        return self.tail

    def __len__(self):
        return 1 + len(self.tail)

    def __iter__(self):
        yield self.head
        yield from self.tail
