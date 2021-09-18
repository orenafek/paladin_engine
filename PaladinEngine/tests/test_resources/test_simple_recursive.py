def f():
    g()
    i()

def g():
    h()

def h():
    pass

def i():
    pass

if __name__ == '__main__':
    f()