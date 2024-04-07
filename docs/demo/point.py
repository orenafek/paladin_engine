class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Point(-1 * self.x, -1 * self.y)

    def __sub__(self, other):
        if isinstance(other, Point):
            return self + (-other)

    def __repr__(self):
        return f'{self.x}, {self.y}'

if __name__ == '__main__':
    point = Point(1,2)
    point.x = 0
    print(point)