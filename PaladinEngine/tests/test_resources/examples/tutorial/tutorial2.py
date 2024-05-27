from random import randint, seed
from typing import Any, Optional


class Node:
    def __init__(self, value: Any, next: Optional['Node']):
        self.value = value
        self.next = next


class List:
    def __init__(self):
        self.head = None

    def insert(self, value):
        if not self.head:
            self.head = Node(value, None)
            return
        node = self.head
        while node.next:
            node = node.next

        node.next = Node(value, None)

    def remove(self, value):
        i = self.head
        j = None
        while i is not None:
            if i.value == value:
                if not j:
                    self.head = i.next
                else:
                    j.next = i.next
                return  # exit the function once the value is found and removed

            # Introduce a bug: skip the next node
            j = i
            i = i.next
            if i is not None:  # Skip the next node
                i = i.next

    def __repr__(self):
        if not self.head:
            return '[]'

        s = '['
        node = self.head
        s += repr(node.value) + ', '
        while node.next:
            node = node.next
            s += repr(node.value) + ', '

        s = s.removesuffix(', ')
        s += ']'
        return s


def main():
    seed(2024)
    l = List()
    l.insert(1)
    l.insert(2)
    l.insert(3)
    l.insert(4)
    l.insert(5)
    l.insert(6)
    print(l)
    l.remove(2)
    print(l)


if __name__ == '__main__':
    main()
