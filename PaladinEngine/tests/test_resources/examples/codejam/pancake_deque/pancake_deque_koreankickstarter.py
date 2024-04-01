from collections import deque


def solution(d: deque) -> int:
    prev = float('-inf')
    curr = 0
    while d:
        if len(d) == 1:
            return curr + (d[0] >= prev)
        elif d[0] < prev and d[-1] < prev:
            d.pop()
            d.popleft()
        elif d[0] >= prev and d[-1] < prev:
            prev = d.popleft()
            curr += 1
        elif d[0] < prev and d[-1] >= prev:
            prev = d.pop()
            curr += 1
        else:
            if d[0] > d[-1]:
                prev = d.pop()
                curr += 1
            else:
                prev = d.popleft()
                curr += 1
    return curr


if __name__ == '__main__':
    path_base = '/Users/oren.afek/Projects/Paladin/paladin_engine/PaladinEngine/' \
                'tests/test_resources/examples/codejam/pancake_deque/ts1_'
    with open(path_base + 'ts1_input.txt', 'r') as input_file, \
            open(path_base + 'output.txt', 'r') as output_file:
        for i in range(int(input_file.readline())):
            n = int(input_file.readline())
            lines = input_file.readline().split()
            d = deque(map(int, lines))
            d = deque([int(x / 1000) for x in d])
            actual = f'Case #{i + 1}: {solution(d)}'
            print(actual)
            if actual != (expected := output_file.readline().strip()):
                raise AssertionError(f'{actual} != {expected}')
