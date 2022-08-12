from random import randint

TIMELINE = []


def p(func):
    global TIMELINE
    TIMELINE.append(func.__name__ + ':')


def e(func):
    global TIMELINE
    TIMELINE.append("~" + func.__name__ + "()")


def dec(func):
    def ff(*args, **kwargs):
        p(func)
        func(*args, **kwargs)
        e(func)

    return ff


@dec
def i():
    TIMELINE.append('i()-body')


@dec
def h():
    TIMELINE.append('h()-body')
    i()


@dec
def g(t: int):
    for i in range(t):
        h()
        TIMELINE.append('g()-body')
        h()


@dec
def f(t: int):
    for i in range(t):
        g(i)


def main():
    f(randint(1, 6))
    prev = None
    curr = prev
    for event in TIMELINE:
        print(f'{curr} \"{event}\"')

        if ':' in event:
            prev = curr
            curr = event

        if '~' in event:
            curr = prev




if __name__ == '__main__':
    main()
