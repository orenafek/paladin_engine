class X(object):
    def __init__(self):
        self._seed = -1

    @property
    def seed(self):
        self._seed += 1
        return self._seed


def main():
    x = X()
    d = {}
    for i in range(10):
        print(f'seed = {x.seed}')
        d[x.seed] = i

if __name__ == '__main__':
    main()