from sudoku_validator import is_valid_entry


def get_empty(board: list[list[int]], empty_indicator: int|str = 0) -> tuple:
    """
    Finds the first empty cell (represented by empty_indicator) in the Sudoku board.

    Args:
        board (list[list[int]]): The 2D list representing the Sudoku board.
        empty_indicator (int | str, optional): The value that indicates an empty cell. Defaults to 0.

    Returns:
        tuple: A tuple containing the row and column index (y, x) of the first empty cell found.
               Returns an empty tuple () if no empty cells are found.
    """
    for y in range(9):
        for x in range(9):
            if board[y][x] == empty_indicator:
                return (y, x)
    else:
        return ()


def get_possible_values(board: list[list[int]], row: int, col: int) -> list:
    """
    Determines the possible valid values that can be placed in a given cell.

    Args:
        board (list[list[int]]): The 2D list representing the Sudoku board.
        row (int): The row index of the cell.
        col (int): The column index of the cell.

    Returns:
        list: A list of integers representing the valid numbers (1-9) that can be placed
              in the specified cell without violating Sudoku rules.
    """
    possible_values = [
        value
        for value in range(1, 10)
        if is_valid_entry(board, row, col, value)
    ]
    return possible_values


def fill_board(board: list[list[int]], empty_indicator: int|str = 0) -> bool:
    """
    Fills the Sudoku board using a backtracking algorithm.

    Args:
        board (list[list[int]]): The 2D list representing the Sudoku board to be filled.
        empty_indicator (int | str, optional): The value that indicates an empty cell. Defaults to 0.

    Returns:
        bool: True if the board can be filled completely according to Sudoku rules, False otherwise.
    """
    empty_cell: tuple = get_empty(board, empty_indicator)
    if empty_cell == ():
        return True

    row_index, col_index = empty_cell
    for value in range(1, 10):
        if is_valid_entry(board, row_index, col_index, value):
            board[row_index][col_index] = value

            # Recursively fill the board
            if fill_board(board, empty_indicator):
                return True

            # When the recursive fails we try another number
            board[row_index][col_index] = empty_indicator
    else:
        # When no possible value was entered
        # Backtrace to the previous cell and retry other numbers
        return False