from stubs.stubs import __FLI__, __POST_CONDITION__, __FC__, __AS__, __FRAME__


import pandas as pd
df = __FC__("pd.read_excel('/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/test_resources/turtle/irobot_kelet.xlsx')", pd.read_excel, locals(), globals(), __FRAME__, 12, '/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/test_resources/turtle/irobot_kelet.xlsx')
__AS__("df = pd.read_excel('/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/test_resources/turtle/irobot_kelet.xlsx')", 'df', locals=locals(), globals=globals(), frame=__FRAME__, line_no=12)
df = __FC__('df.dropna()', df.dropna, locals(), globals(), __FRAME__, 19)
__AS__('df = df.dropna()', 'df', locals=locals(), globals=globals(), frame=__FRAME__, line_no=12)
df = __FC__('df.transpose()', df.transpose, locals(), globals(), __FRAME__, 24)
__AS__('df = df.transpose()', 'df', locals=locals(), globals=globals(), frame=__FRAME__, line_no=12)
__FC__('print(df)', print, locals(), globals(), __FRAME__, 29, df)
walls = [__FC__('tuple(x)', tuple, locals(), globals(), __FRAME__, 34, x) for x in __FC__('df.values.tolist()', df.values.tolist, locals(), globals(), __FRAME__, 34)[1:]]
__AS__('walls = [tuple(x) for x in df.values.tolist()[1:]]', 'walls', locals=locals(), globals=globals(), frame=__FRAME__, line_no=12)
start = (4, 7)
__AS__('start = (4, 7)', 'start', locals=locals(), globals=globals(), frame=__FRAME__, line_no=12)
robot_pos = start
__AS__('robot_pos = start', 'robot_pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=12)
robot_dir = (1, 0)
__AS__('robot_dir = (1, 0)', 'robot_dir', locals=locals(), globals=globals(), frame=__FRAME__, line_no=12)

def add_v(x, y):
    return (x[0] + y[0], x[1] + y[1])

def Move():
    """ Returns True if moves, False it hits wall"""
    global robot_pos
    next_temp = __FC__('add_v(robot_pos, robot_dir)', add_v, locals(), globals(), __FRAME__, 56, robot_pos, robot_dir)
    __AS__('next_temp = add_v(robot_pos, robot_dir)', 'next_temp', locals=locals(), globals=globals(), frame=__FRAME__, line_no=56)
    if next_temp not in walls:
        robot_pos = next_temp
        __AS__('robot_pos = next_temp', 'robot_pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=58)
        __FC__('print(robot_pos)', print, locals(), globals(), __FRAME__, 59, robot_pos)
        return True
    else:
        return False

def RotateRight():
    global robot_dir
    __FC__("print('rotate')", print, locals(), globals(), __FRAME__, 68, 'rotate')
    if robot_dir == (1, 0):
        robot_dir = (0, -1)
        __AS__('robot_dir = (0, -1)', 'robot_dir', locals=locals(), globals=globals(), frame=__FRAME__, line_no=70)
    elif robot_dir == (0, -1):
        robot_dir = (-1, 0)
        __AS__('robot_dir = (-1, 0)', 'robot_dir', locals=locals(), globals=globals(), frame=__FRAME__, line_no=72)
    elif robot_dir == (-1, 0):
        robot_dir = (0, 1)
        __AS__('robot_dir = (0, 1)', 'robot_dir', locals=locals(), globals=globals(), frame=__FRAME__, line_no=74)
    else:
        robot_dir = (1, 0)
        __AS__('robot_dir = (1, 0)', 'robot_dir', locals=locals(), globals=globals(), frame=__FRAME__, line_no=76)

def IrobotClean():
    start_pos = (0, 0)
    __AS__('start_pos = (0, 0)', 'start_pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=86)
    current_pos = start_pos
    __AS__('current_pos = start_pos', 'current_pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=86)
    direction = (1, 0)
    __AS__('direction = (1, 0)', 'direction', locals=locals(), globals=globals(), frame=__FRAME__, line_no=86)

    def add_v(x, y):
        return (x[0] + y[0], x[1] + y[1])
    Edges = {}
    __AS__('Edges = {}', 'Edges', locals=locals(), globals=globals(), frame=__FRAME__, line_no=86)
    visited = {start_pos}
    __AS__('visited = {start_pos}', 'visited', locals=locals(), globals=globals(), frame=__FRAME__, line_no=86)
    while __FC__('has_unexplored(visited, Edges)', has_unexplored, locals(), globals(), __FRAME__, 98, visited, Edges):
        next_pos = __FC__('add_v(current_pos, direction)', add_v, locals(), globals(), __FRAME__, 99, current_pos, direction)
        __AS__('next_pos = add_v(current_pos, direction)', 'next_pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=99)
        if next_pos not in visited:
            __FC__('visited.add(next_pos)', visited.add, locals(), globals(), __FRAME__, 102, next_pos)
        status = __FC__('Move()', Move, locals(), globals(), __FRAME__, 104)
        __AS__('status = Move()', 'status', locals=locals(), globals=globals(), frame=__FRAME__, line_no=99)
        Edges[current_pos, next_pos] = status
        __AS__('Edges[current_pos, next_pos] = status', "Edges[('current_pos', 1):('next_pos', 1)]", locals=locals(), globals=globals(), frame=__FRAME__, line_no=99)
        if status:
            current_pos = next_pos
            __AS__('current_pos = next_pos', 'current_pos', locals=locals(), globals=globals(), frame=__FRAME__, line_no=110)
        else:
            __FC__('RotateRight()', RotateRight, locals(), globals(), __FRAME__, 114)
            if direction == (1, 0):
                direction = (0, -1)
                __AS__('direction = (0, -1)', 'direction', locals=locals(), globals=globals(), frame=__FRAME__, line_no=116)
            elif direction == (0, -1):
                direction = (-1, 0)
                __AS__('direction = (-1, 0)', 'direction', locals=locals(), globals=globals(), frame=__FRAME__, line_no=118)
            elif direction == (-1, 0):
                direction = (0, 1)
                __AS__('direction = (0, 1)', 'direction', locals=locals(), globals=globals(), frame=__FRAME__, line_no=120)
            else:
                direction = (1, 0)
                __AS__('direction = (1, 0)', 'direction', locals=locals(), globals=globals(), frame=__FRAME__, line_no=122)

def has_unexplored(visited, edges):
    __iter_1 = visited.__iter__()
    while True:
        try:
            (x, y) = __iter_1.__next__()
        except StopIteration:
            break
        l = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        __AS__('l = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]', 'l', locals=locals(), globals=globals(), frame=__FRAME__, line_no=130)
        __iter_0 = l.__iter__()
        while True:
            try:
                p = __iter_0.__next__()
            except StopIteration:
                break
            if p not in visited and ((x, y), p) not in edges:
                return True
    return False
__FC__('IrobotClean()', IrobotClean, locals(), globals(), __FRAME__, 141)