from typing import Any


def lists():
    l1 = [1, 2, 3, 4, 5]
    print(l1)
    l1.append(6)
    l1.remove(3)
    l1.reverse()
    print(l1)
    l1.clear()
    l1.extend([6, 7, 8, 9, 10])


def sets():
    s1 = {1, 2, 3}
    print(s1)
    s1.add(4)
    print(s1)
    s1.remove(1)
    print(s1)
    s1.update({3, 4, 5})
    print(s1)
    s1.difference_update({5, 7})
    print(s1)
    s1.discard(6)
    print(s1)
    s1.discard(3)
    print(s1)
    s1.update({1, 2, 3, 4, 5})
    print(s1)
    s1.intersection_update({3, 4, 5, 10})
    print(s1)
    s1.symmetric_difference_update({5, 6, 7})
    print(s1)
    s1.clear()
    print(s1)


def tuples():
    t1 = (1, 2, 3,)
    print(t1)


def dicts():
    d1 = {1: 'a', 2: 'b', 3: 'c'}
    print(d1)

    class Hashable(object):
        def __init__(self, value: Any):
            self.value: Any = value

        def __hash__(self):
            return hash(self.value)

        def __repr__(self):
            return repr(self.value)

    class HashableDict(dict):
        def __hash__(self):
            return sum([hash(k) for k in self.keys()]) + sum([hash(v) for v in self.values()])

    d2 = {Hashable('A'): 1,
          Hashable('B'): 2}

    print(d2)

    d3 = {HashableDict([('A', 1), ('B', 2)]): 3}
    print(d3)

def main():
    lists()
    sets()
    tuples()
    dicts()


if __name__ == '__main__':
    main()
