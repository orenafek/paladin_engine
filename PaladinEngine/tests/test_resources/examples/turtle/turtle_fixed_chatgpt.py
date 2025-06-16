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
    """ Add two vectors. """
    return (x[0] + y[0], x[1] + y[1])


def Move():
    """ Returns True if moves, False if hits wall. """
    global robot_pos

    # Calculate next possible position of robot after moving
    next_pos = add_v(robot_pos, robot_dir)
    if next_pos not in walls:
        robot_pos = next_pos
        print(robot_pos)
        return True
    else:
        return False


def RotateRight():
    """ Rotate the robot's direction 90 degrees clockwise. """
    global robot_dir
    direction_mapping = {
        (1, 0): (0, -1),
        (0, -1): (-1, 0),
        (-1, 0): (0, 1),
        (0, 1): (1, 0)
    }
    robot_dir = direction_mapping[robot_dir]
    print("Rotate to", robot_dir)


def has_unexplored(visited, edges):
    """ Check if there are unexplored points. """
    for (x, y) in visited:
        for dx, dy in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
            p = (x + dx, y + dy)
            if p not in visited:
                return True  # There is still unexplored point
    return False  # No more points to explore


def IrobotClean():
    """ Main cleaning logic. """
    current_pos = start
    visited = {current_pos}
    edges = {}

    while has_unexplored(visited, edges):
        next_pos = add_v(current_pos, robot_dir)

        if next_pos not in visited:
            visited.add(next_pos)

        if not Move():  # If it hits a wall or cannot move
            RotateRight()

        current_pos = robot_pos  # Update the current position after a move or rotate


def main():
    """ Entry point of the program. """
    IrobotClean()


if __name__ == '__main__':
    main()
