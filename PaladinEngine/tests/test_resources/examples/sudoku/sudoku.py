BOARD_SIZE = 4
POSSIBLE_NUMBERS = set(range(1, BOARD_SIZE + 1))


def is_valid(board, row, col, num):
    # Check row
    if num in board[row]:
        return False

    # Check column
    for i in range(BOARD_SIZE):
        if board[i][col] == num:
            return False

    # Check 2x2 subgrid
    start_row, start_col = 2 * (row // 2), 2 * (col // 2)
    for i in range(start_row, start_row + 2):
        for j in range(start_col, start_col + 2):
            if board[i][j] == num:
                return False

    # Check diagonals
    if row == col:
        for i in range(BOARD_SIZE):
            if board[i][i] == num:
                return False
    if row + col == BOARD_SIZE - 1:
        for i in range(BOARD_SIZE):
            if board[i][-i] == num:
                return False

    return True


def find_empty_location(board):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                return i, j
    return -1, -1


def solve_sudoku(board):
    row, col = find_empty_location(board)

    if row == -1 and col == -1:
        return True

    for num in POSSIBLE_NUMBERS:
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0

    return False


def print_board(board):
    for row in board:
        print(" ".join(str(cell) for cell in row))


# Example puzzle
puzzle = [
    [0, 0, 0, 0],
    [0, 3, 0, 0],
    [0, 0, 0, 4],
    [1, 0, 0, 0]
]

if solve_sudoku(puzzle):
    print("Solution:")
    print_board(puzzle)
else:
    print("No solution exists.")
