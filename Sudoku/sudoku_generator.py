import sudoku_solver
from sudoku_validator import is_valid_entry
import random


def count_solutions(
    board: list[list[int]],
    limit=2,
    empty_indicator: int|str = 0
) -> int:
    """
    Counts the number of distinct solutions for a given Sudoku board.

    The function employs a backtracking approach to explore possible solutions.
    It can be configured to stop counting once a specified number of solutions
    ('limit') is reached, which can be useful for determining if a puzzle has
    a unique solution or multiple solutions without needing to find all of them.

    Args:
        board (list[list[int]]): The 2D list representing the Sudoku board.
        limit (int, optional): The maximum number of solutions to count.
                               The counting stops early if this limit is reached. Defaults to 2.
        empty_indicator (int | str, optional): The value that indicates an empty cell. Defaults to 0.

    Returns:
        int: The number of distinct solutions found, up to the specified 'limit'.
             Returns a value greater than or equal to 'limit' if that many or more
             solutions exist.
    """
    empty_cell = sudoku_solver.get_empty(board, empty_indicator)
    if not empty_cell:
        return 1

    row, col = empty_cell
    count = 0
    for num in range(1, 10):
        if is_valid_entry(board, row, col, num):
            board[row][col] = num
            count += count_solutions(board, limit, empty_indicator)
            board[row][col] = empty_indicator
            if count >= limit:
                break  # No need to count further if more than one solution
    return count


def _create_unique_board(
    board:list[list[int]], 
    total_empties:int, 
    empty_indicator: int|str = 0
) -> None:
    """
    Modifies a full Sudoku board to create a puzzle with a unique solution.
    Randomly removes cells while ensuring that the board has exactly one solution,
    up to the specified number of empty cells.

    Args:
        board (list[list[int]]): A completed 9x9 Sudoku board.
        total_empties (int): Target number of empty cells to create.
    """
    # Remove numbers while checking for unique solution
    attempts = 0
    max_attempts = 81 * 3  # prevent infinite loop
    empties = 0

    while empties < total_empties and attempts < max_attempts:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if board[row][col] == empty_indicator:
            attempts += 1
            continue

        backup_value = board[row][col]
        board[row][col] = empty_indicator

        board_copy = [r.copy() for r in board]
        solutions = count_solutions(board_copy, 2, empty_indicator)

        if solutions == 1:
            empties += 1
        else:
            board[row][col] = backup_value  # revert
        attempts += 1


def generate(
    total_empties:int=45, 
    unique:bool=False, 
    empty_indicator:int|str = 0
) -> tuple[list[list[int]]]:
    """
    Generates a Sudoku board with the specified number of empty cells.

    Args:
        total_empties (int): Number of empty cells to include.
        unique (bool): If True, ensures the board has a unique solution.

    Returns:
        A tuple containing the generated Sudoku board and a solved board.

    Note:
        Using unique=True with total_empties > 50 may slow generation.
        For total_empties > 55, uniqueness is not guaranteed.
    """
    board = [[empty_indicator for _ in range(9)] for _ in range(9)]
    if not 0 < total_empties <= 81:
        raise ValueError(f"Expected a value between 1 and 81 but got {total_empties}.")
   
    # Randomly choose 3 cells/squares in first row, and fill them with a random value
    # between 1 and 9, this makes every board unique
    # Otherwise first row will always be 1,2,3,4,5,6,7,8,9
    cells = random.sample([i for i in range(9)], k=3)
    values = random.sample([i for i in range(1, 10)], k=3)
    for col, value in zip(cells, values):
        board[0][col] = value

    # Solve the board
    sudoku_solver.fill_board(board, empty_indicator)
    solved_board = [row.copy() for row in board]

    if unique:
        _create_unique_board(board, total_empties, empty_indicator)

    else:
        # Remove some numbers to create the puzzle
        while total_empties > 0: 
            row, col = random.randint(0, 8), random.randint(0, 8)
            if board[row][col] == empty_indicator:
                continue

            board[row][col] = empty_indicator
            total_empties -= 1

    return board, solved_board