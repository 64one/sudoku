# This validates sudoku boards and user input to the board


def get_values_in_square(
    board: list[list[int]],
    row_index: int,
    col_index: int
) -> list[int]:
    """
    Returns a list of all values present in the 3x3 subgrid (square)
    that contains the given row and column index.

    Args:
        board (list[list[int]]): The 2D list representing the Sudoku board.
        row_index (int): The row index of a cell within the square.
        col_index (int): The column index of a cell within the square.

    Returns:
        list[int]: A list containing all the integer values found within the 3x3 square.
    """
    y = (row_index // 3) * 3
    x = (col_index // 3) * 3
    square = []
    for i in range(3):
        square += board[y + i][x: x + 3]

    return square


def is_valid_entry(
    board: list[list[int]],
    row_index: int,
    col_index: int,
    value: int
) -> bool:
    """
    Checks if a given value is a valid entry for a specific cell in the Sudoku board
    according to Sudoku rules (not present in the same row, column, or 3x3 square).

    Args:
        board (list[list[int]]): The 2D list representing the Sudoku board.
        row_index (int): The row index of the cell to check.
        col_index (int): The column index of the cell to check.
        value (int): The integer value to validate for the cell.

    Returns:
        bool: True if the value is a valid entry for the cell, False otherwise.
    """
    column = [row[col_index] for row in board]
    row = board[row_index]
    square = get_values_in_square(board, row_index, col_index)

    if value in column + row + square:
        return False
    else:
        return True


def is_valid_board(
    board: list[list[int]],
    empty_indicator: int|str = 0
) -> bool:
    """
    Validates if the current state of the entire Sudoku board is valid
    according to Sudoku rules (no duplicates in any row, column, or 3x3 square),
    ignoring cells marked as empty.

    Args:
        board (list[list[int]]): The 2D list representing the Sudoku board to validate.
        empty_indicator (int | str, optional): The value that indicates an empty cell. Defaults to 0.

    Returns:
        bool: True if the board is currently valid, False otherwise.
    """
    if len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("Board is not a 9x9.")

    for row in range(9):
        for col in range(9):
            value = board[row][col]
            # We don't check for empty cells as they have duplicates in unsolved boards
            if value == empty_indicator:
                continue

            # Temporary set this cell as empty to avoid matching against itself
            # thereby detecting false duplicate
            board[row][col] = empty_indicator
            if not is_valid_entry(board, row, col, value):
                return False

            # Reset the cell back to original value
            board[row][col] = value
    else:
        # The board has passed validation
        return True