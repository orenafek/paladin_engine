#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Uses https://github.com/rkistner/contest-algorithms
import os
import re


def solution(input_file):
    output = []
    T = int(input_file.readline())
    for case in range(1, T + 1):
        r, c = map(int, input_file.readline().split())

        moves, swap = solve(r, c)
        if not moves:
            moves, swap = solve(r, c, True)

        if moves:
            output.append("Case #%d: %s" % (case, "POSSIBLE"))
            for x, y in moves:
                if swap:
                    x, y = y, x
                output.append(f'{y + 1} {x + 1}')
        else:
            output.append("Case #%d: %s" % (case, "IMPOSSIBLE"))

    return output


def solve(r, c, try2=False):
    swap = False
    if c > r:
        r, c = c, r
        swap = True
    if r <= 3:
        return None, False
    if (r, c) == (4, 2):
        return None, False

    grid = [[False] * c for i in range(r)]

    x, y = 0, 0
    moves = []
    for i in range(r * c):
        x2 = (x + 1) % c
        if x2 == 0 and try2:
            y2 = 0
        else:
            y2 = (y + 1) % r
        y3 = y2
        while grid[y2][x2] or y2 == y or y2 + x2 == y + x or y2 - x2 == y - x:
            y2 = (y2 + 1) % r
            if y2 == y3:
                return None, swap

        grid[y2][x2] = True
        x, y = (x2, y2)
        moves.append((x, y))
    return moves, swap


def main():
    path_base = '/Users/oren.afek/Projects/Paladin/paladin_engine/PaladinEngine/tests/test_resources/examples/codejam/pylons/'
    input_path = os.path.join(path_base, "ts1_input.txt")
    output_path = os.path.join(path_base, "ts1_output.txt")

    # Read the input from the file
    with open(input_path, "r") as input_file, open(output_path, 'r') as output_file:
        solution_output_lines = [l.strip() for l in output_file.readlines()]
        submission_output_lines = solution(input_file)

    prev_sol = None
    for i, x in enumerate(zip(submission_output_lines, solution_output_lines)):
        sub_line, sol_line = x
        if re.match("Case.*", sol_line):
            if sub_line != sol_line:
                raise AssertionError(f"found diff in line {i + 1} of output files")
            prev_sol = None
        elif prev_sol:
            cur_sol = [int(x) for x in sub_line.split(" ")]
            if cur_sol[0] == prev_sol[0] or cur_sol[1] == prev_sol[1]:
                raise AssertionError('Jumped in same row or column')

            if (cur_sol[1] - cur_sol[0]) == (prev_sol[1] - prev_sol[0]) or (cur_sol[1] + cur_sol[0]) == (prev_sol[1] + prev_sol[0]):
                raise AssertionError('Jumped in diagonal')
            prev_sol = cur_sol
        else:
            prev_sol = [int(x) for x in sub_line.split(" ")]

    if i != len(submission_output_lines) - 1:
        raise Exception("submission has extra lines")
    if i != len(solution_output_lines) - 1:
        raise Exception("submission missing lines")


if __name__ == '__main__':
    main()
