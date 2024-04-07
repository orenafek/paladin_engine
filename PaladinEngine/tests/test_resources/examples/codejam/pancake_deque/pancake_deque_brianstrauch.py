def solve(n, ps):
    ans = 0

    p = 0
    i = 0
    j = n - 1

    while i <= j:
        if ps[i] >= p and (ps[i] < ps[j] or ps[j] < p):
            p = ps[i]
            i += 1
        elif ps[j] >= p:
            p = ps[j]
            j -= 1
        else:
            break

        ans += 1

    return ans


if __name__ == '__main__':
    path_base = '/Users/oren.afek/Projects/Paladin/paladin_engine/PaladinEngine/' \
                'tests/test_resources/examples/codejam/pancake_deque/ts1_'
    with open(path_base + 'ts1_input.txt', 'r') as input_file, \
            open(path_base + 'output.txt', 'r') as output_file:
        for i in range(int(input_file.readline())):
            n = int(input_file.readline())
            lines = input_file.readline().split()
            ps = list(map(int, lines))
            actual = f'Case #{i + 1}: {solve(n, ps)}'
            print(actual)
            if actual != (expected := output_file.readline().strip()):
                raise AssertionError(f'{actual} != {expected}')
