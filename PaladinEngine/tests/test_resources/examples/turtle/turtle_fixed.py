from stubs.stubs import __PAUSE__, __RESUME__

__PAUSE__()
import pandas as pd

df = pd.read_excel(
    '/Users/oren.afek/Projects/Paladin/paladin_engine/PaladinEngine/tests/test_resources/examples/turtle/irobot_kelet.xlsx')

df = df.dropna()
df = df.transpose()
print(df)

__RESUME__()
walls = [(int(x[0]), int(x[1])) for x in df.values.tolist()[1:]]
start = (4, 7)
robot_pos = start
robot_dir = (1, 0)


def add_v(x, y):
    return (x[0] + y[0], x[1] + y[1])


# for the testing part
def Move():
    """ Returns True if moves, False it hits wall"""
    global robot_pos

    # next possible position of robot after moving
    next_temp = add_v(robot_pos, robot_dir)
    if next_temp not in walls:
        robot_pos = next_temp
        print(robot_pos)
        return True
    else:
        return False


def RotateRight():
    global robot_dir
    print("rotate")
    if robot_dir == (1, 0):
        robot_dir = (0, -1)
    elif robot_dir == (0, -1):
        robot_dir = (-1, 0)
    elif robot_dir == (-1, 0):
        robot_dir = (0, 1)
    else:
        robot_dir = (1, 0)


def IrobotClean():
    global start, robot_dir
    # defining the edges for the irobot
    start_pos = start
    current_pos = start_pos
    direction = robot_dir

    def add_v(x, y):
        return (x[0] + y[0], x[1] + y[1])

    # is there a path between a,b
    Edges = {}

    visited = {start_pos}

    while has_unexplored(visited, Edges):
        next_pos = add_v(current_pos, direction)

        if next_pos not in visited:
            visited.add(next_pos)

        status = Move()
        # TODO: A Fix.
        Edges[(current_pos, next_pos)] = status

        # updating position - no wall

        if status:
            current_pos = next_pos

        # updating the direction  - hit a wall
        else:
            RotateRight()
            # direction = robot_dir
            if direction == (1, 0):
                direction = (0, -1)
            elif direction == (0, -1):
                direction = (-1, 0)
            elif direction == (-1, 0):
                direction = (0, 1)
            else:
                direction = (1, 0)

        # In[10]:


# checking if there are unexplored points
def has_unexplored(visited, edges):
    for (x, y) in visited:
        l = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        for p in l:
            if p not in visited and ((x, y), p) not in edges:
                return True  # there are still unexplored points, p is unexplored

    return False  # there aren't otherb points to explore     


def main():
    IrobotClean()


if __name__ == '__main__':
    main()
