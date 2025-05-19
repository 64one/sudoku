import copy
import random
from typing import List, Tuple, Optional

import sudoku_validator
import sudoku_generator


class SudokuBoard:
    """
    Represents a Sudoku board with its current state, unsolved initial state,
    and the solved version. Provides methods for validation, modification,
    and retrieval of board information.
    """
    def __init__(
        self,
        unsolved_board: List[List[int]],
        solved_board: List[List[int]],
        empty_indicator: int = 0,
    ):
        """
        Initializes a SudokuBoard instance.

        Args:
            unsolved_board (List[List[int]]): A 9x9 2D list representing the initial,
                unsolved state of the Sudoku puzzle. Empty cells should be
                indicated by the `empty_indicator`.
            solved_board (List[List[int]]): A 9x9 2D list representing the fully
                solved version of the Sudoku puzzle.
            empty_indicator (int, optional): The integer value used to represent
                empty cells on the board. Defaults to 0.

        Raises:
            IndexError: If either `unsolved_board` or `solved_board` is not a
                9x9 list of lists.
            ValueError: If either input board contains invalid values (not in
                range 1-9 or the `empty_indicator`), if the `solved_board`
                contains empty cells, or if the `solved_board` is not a valid
                solution to the `unsolved_board`.
        """
        self.empty_indicator = empty_indicator
        self._rows = 9  # Total inner lists
        self._columns = 9  # Total values per inner list

        self._validate_input_boards(unsolved_board, "UnsolvedBoard")
        self._validate_input_boards(solved_board, "SolvedBoard")
        self._is_solved_version(unsolved_board, solved_board)

        self._board = copy.deepcopy(unsolved_board)
        self._unsolved_board = copy.deepcopy(unsolved_board)
        self._solved_board = copy.deepcopy(solved_board)

        # These are squares whose values should never be changed
        self.prefilled_squares: Tuple[Tuple[int, int], ...] = tuple(
            (row, col)
            for row in range(self._rows)
            for col in range(self._columns)
            if self._unsolved_board[row][col] != self.empty_indicator
        )
        # These are squares the player is supposed to update their values
        self.player_fillable_squares: Tuple[Tuple[int, int], ...] = tuple(
            (row, col)
            for row in range(self._rows)
            for col in range(self._columns)
            if self._unsolved_board[row][col] == self.empty_indicator
        )
        # These are non empty squares where user has added a value
        # This list allows undo and deleted values of selected square
        self.edited_squares: List[Tuple[int, int]] = []

    def _validate_input_boards(
        self,
        board: List[List[int]],
        board_name: str
    ) -> None:
        """
        Validates if the given board has the correct dimensions (9x9) and
        contains only valid Sudoku values.

        Args:
            board (List[List[int]]): The Sudoku board to validate.
            board_name (str): A descriptive name for the board being validated
                (e.g., "UnsolvedBoard", "SolvedBoard").

        Raises:
            IndexError: If the board is not a 9x9 list of lists.
            ValueError: If the board contains invalid values or is not a valid
                Sudoku board according to `self.is_valid_board()`. Additionally,
                if `board_name` is "SolvedBoard" and it contains empty values.
        """
        if len(board) != self._rows or any(len(row) != self._columns for row in board):
            raise IndexError(f"Sudoku board ({board_name}) must be a {self._columns} x {self._rows}")

        if not self.is_valid_board(board=board):
            raise ValueError(f"{board_name} is incorrectly filled.")

        # Validate that solved board is fully solved
        if board_name == "SolvedBoard" and self.total_empty_squares(board=board) != 0:
            raise ValueError("SolvedBoard should not have empty values.")

        # Validate every value
        for row in range(self._rows):
            for col in range(self._columns):
                value = board[row][col]
                if value != self.empty_indicator and value not in range(1, 10):
                    raise ValueError(f"invalid value -> {value} at {board_name}[{row}][{col}]")

    def _is_solved_version(
        self,
        unsolved_board: List[List[int]],
        solved_board: List[List[int]]
    ) -> None:
        """
        Validates that the `solved_board` is indeed a solved version of the
        `unsolved_board`, meaning that all the pre-filled values in the
        `unsolved_board` are the same in the `solved_board`.

        Args:
            unsolved_board (List[List[int]]): The initial unsolved Sudoku board.
            solved_board (List[List[int]]): The purported solved version of the board.

        Raises:
            ValueError: If the `solved_board` does not match the pre-filled
                values of the `unsolved_board`.
        """
        for row in range(self._rows):
            for col in range(self._columns):
                unsolved_value = unsolved_board[row][col]
                solved_value = solved_board[row][col]
                if unsolved_value != self.empty_indicator and unsolved_value != solved_value:
                    raise ValueError("SolvedBoard is not a solved version of UnsolvedBoard.")

    def is_valid_board(
        self,
        board: Optional[List[List[int]]] = None,
        expected_empties: Optional[int] = None
    ) -> bool:
        """
        Validates whether the given board (or the current board if none is provided)
        is a valid Sudoku puzzle according to Sudoku rules, and optionally checks
        if the number of empty squares matches an expected value.

        Args:
            board (Optional[List[List[int]]], optional): The board to validate.
                If None, the current `self._board` is used. Defaults to None.
            expected_empties (Optional[int], optional): The expected number of
                empty squares on the board. If provided, the validation will
                also check if the actual number of empty squares matches this value.
                Defaults to None.

        Returns:
            bool: True if the board is a valid Sudoku puzzle and (if
                `expected_empties` is provided) has the expected number of
                empty squares, False otherwise.

        Raises:
            TypeError: If `board` is not a list or if `expected_empties` is not
                an integer or None.
        """
        board = board if board is not None else self._board
        if not isinstance(board, list):
            raise TypeError(f"board must be of type list not {type(board).__name__}")

        if not isinstance(expected_empties, (int, type(None))):
            raise TypeError(f"expected_empties must be an int or None, not {type(expected_empties).__name__}")

        actual_empties = self.total_empty_squares(board=board)
        valid_empties = (actual_empties == expected_empties) if expected_empties != None else True  # 0 is valid
        valid_board = sudoku_validator.is_valid_board(board, self.empty_indicator)

        return valid_board and valid_empties

    def is_valid_entry(self, row: int, col: int, value: int) -> bool:
        """
        Validates if placing the given `value` at the specified `row` and `col`
        on the current board would result in a valid Sudoku entry (no conflicts
        in the same row, column, or 3x3 subgrid). Also prevents overwriting
        pre-filled squares or entering an already present empty value.

        Args:
            row (int): The row index (0-8) of the cell to check.
            col (int): The column index (0-8) of the cell to check.
            value (int): The value (1-9) to be placed in the cell.

        Returns:
            bool: True if the entry is valid, False otherwise.

        Raises:
            IndexError: If `row` or `col` are not within the valid range (0-8).
            ValueError: If `value` is not within the valid range (1-9).
        """
        if not (0 <= row < self._rows and 0 <= col < self._columns):
            raise IndexError(f"Row and column must be in the range 0–{self._rows - 1}.")

        if not (1 <= value <= 9):
            raise ValueError("Value must be in the range of 1-9")

        if (row, col) in self.prefilled_squares:
            return False  # Prevent overwriting prefilled values

        elif value == self.empty_indicator == self.get_value(row, col):
            return False  # Value is already empty, don't allow edit

        return sudoku_validator.is_valid_entry(self._board, row, col, value)

    def reset_board(self) -> List[List[int]]:
        """
        Resets the current board (`self._board`) to its original unsolved state
        (`self._unsolved_board`) and clears the list of edited squares.

        Returns:
            List[List[int]]: The reset Sudoku board.
        """
        self._board = copy.deepcopy(self._unsolved_board)
        self.edited_squares.clear()
        return self._board

    def update_to_solved(self) -> None:
        """
        Updates the current board (`self._board`) to the fully solved version
        (`self._solved_board`) and clears the list of edited squares.
        """
        self._board = copy.deepcopy(self._solved_board)
        self.edited_squares.clear()

    def get_current_board(self) -> List[List[int]]:
        """
        Returns a copy of the current state of the Sudoku board.

        Returns:
            List[List[int]]: The current Sudoku board.
        """
        return self._board

    def total_empty_squares(self, board: Optional[List[List[int]]] = None) -> int:
        """
        Calculates the total number of empty squares on the given board (or the
        current board if none is provided).

        Args:
            board (Optional[List[List[int]]], optional): The board to count
                empty squares on. If None, the current `self._board` is used.
                Defaults to None.

        Returns:
            int: The total number of empty squares (cells with the
            `self.empty_indicator`).
        """
        board = board if board is not None else self._board
        return sum(row.count(self.empty_indicator) for row in board)

    def has_one_solution(self) -> bool:
        """
        Determines whether the current unsolved board has exactly one unique
        solution. This typically involves using a Sudoku solving algorithm to
        count the number of possible solutions.

        Returns:
            bool: True if the board has a single unique solution, False otherwise.
        """
        solutions = sudoku_generator.count_solutions(self.get_board_copy())
        return (solutions == 1)

    def get_hint(self) -> Tuple[int, int, int]:
        """
        Selects a random empty cell that was not pre-filled and has not been
        edited by the player yet, and returns the correct value for that cell
        from the solved board along with its row and column.

        Returns:
            Tuple[int, int, int]: A tuple containing:
                - value (int): The correct value for the selected cell (0 if no
                  valid hint is available, e.g., if the board is full or no
                  unedited empty cells exist).
                - row (int): The row index of the selected cell.
                - col (int): The column index of the selected cell.
        """
        if self.total_empty_squares() == 0:
            return (0, 0, 0)

        empty_squares = [
            square
            for square in self.player_fillable_squares
            if square not in self.edited_squares
        ]

        if not empty_squares:
            return (0, 0, 0)  # No unedited empty squares available

        row, col = random.choice(empty_squares)
        value = self._solved_board[row][col]

        return (value, row, col)

    def is_currently_empty(self, row: int, col: int) -> bool:
        """
        Checks if the cell at the specified `row` and `col` on the current
        board is currently empty (contains the `self.empty_indicator`).

        Args:
            row (int): The row index (0-8) of the cell to check.
            col (int): The column index (0-8) of the cell to check.

        Returns:
            bool: True if the cell is empty, False otherwise.

        Raises:
            IndexError: If `row` or `col` are not within the valid range (0-8).
        """
        if not (0 <= row < self._rows and 0 <= col < self._columns):
            raise IndexError(f"Row and column must be in the range 0–{self._rows - 1}.")

        return (self.get_value(row, col) == self.empty_indicator)

    def get_value(self, row: int, col: int) -> int:
        """
        Returns the current value of the cell at the specified `row` and `col`
        on the current board.

        Args:
            row (int): The row index (0-8) of the cell.
            col (int): The column index (0-8) of the cell.

        Returns:
            int: The value in the cell.

        Raises:
            IndexError: If `row` or `col` are not within the valid range (0-8).
        """
        if not (0 <= row < self._rows and 0 <= col < self._columns):
            raise IndexError(f"Row and column must be in the range 0–{self._rows - 1}.")

        return self._board[row][col]

    def set_value(self, row: int, col: int, value: int) -> bool:
        """
        Sets the value of the cell at the specified `row` and `col` on the
        current board to the given `value`, provided the entry is valid
        according to Sudoku rules and the cell is not a pre-filled square.
        If the value is successfully set in a previously empty cell, the
        cell's coordinates are added to the `edited_squares` list. Allows
        swapping non-empty values in player-fillable squares.

        Args:
            row (int): The row index (0-8) of the cell to set.
            col (int): The column index (0-8) of the cell to set.
            value (int): The value (1-9) to set in the cell.

        Returns:
            bool: True if the value was successfully set, False otherwise
            (e.g., if the entry is invalid or the cell is pre-filled).

        Raises:
            IndexError: If `row` or `col` are not within the valid range (0-8).
            ValueError: If `value` is not within the valid range (1-9).
        """
        if not (0 <= row < self._rows and 0 <= col < self._columns):
            raise IndexError(f"Row and column must be in the range 0–{self._rows - 1}.")
        if not (1 <= value <= 9):
            raise ValueError("Value must be in the range of 1-9")

        if self.is_valid_entry(row, col, value):
            self._board[row][col] = value
            square = (row, col)
            # Don't readd the square when swapping values as it's already added
            if square not in self.edited_squares and self._unsolved_board[row][col] == self.empty_indicator and value != self.empty_indicator:
                self.edited_squares.append((row, col))
            return True

        return False

    def set_empty(self, row: int, col: int) -> bool:
        """
        Updates a specified square on the board to empty.

        This method should be called when a value that was previously added
        to a square (that was initially empty at the start of the game)
        is being cleared.

        Args:
            row (int): The row index of the square (0-indexed).
            col (int): The column index of the square (0-indexed).

        Returns:
            bool: True if the square was successfully set to empty (i.e.,
                  it was in the set of edited squares), False otherwise.

        Raises:
            IndexError: If the provided row or column index is out of bounds
                        for the board dimensions.
        """
        if not (0 <= row < self._rows and 0 <= col < self._columns):
            raise IndexError(f"Row and column must be in the range 0–{self._rows - 1}.")

        square = (row, col)
        if square in self.edited_squares:
            self._board[row][col] = self.empty_indicator
            self.edited_squares.remove(square)
            return True
        return False

    def get_by_value(self, value: int) -> Tuple[tuple[int, int]]:
        """
        Finds all squares on the board that contain a specific value.

        Args:
            value (int): The value to search for (must be between 1 and 9 inclusive).

        Returns:
            Tuple[tuple[int, int], ...]: A tuple containing the (row, column)
                                         coordinates of all squares with the given value.
                                         Returns an empty tuple if no such squares are found.

        Raises:
            ValueError: If the provided value is not within the valid Sudoku range (1-9).
        """
        if not (1 <= value <= 9):
            raise ValueError("Value must be in the range of 1-9")

        squares = tuple(
            (row, col)
            for row in range(self._rows)
            for col in range(self._columns)
            if self.get_value(row, col) == value
        )
        return squares

    def find_conflicts(self, row: int, col: int, value: int) -> list[tuple[int, int]]:
        """
        Identifies conflicting cells based on a given cell and value.

        A conflict occurs if another cell in the same row, column, or 3x3 subgrid
        contains the same value. The method excludes the given cell itself from
        the conflict check.

        Args:
            row (int): The row index of the cell to check (0-indexed).
            col (int): The column index of the cell to check (0-indexed).
            value (int): The value to check for conflicts (must be between 1 and 9 inclusive).

        Returns:
            List[tuple[int, int], ...]: A list of (row, column) coordinates of cells
                                         that conflict with the given cell and value.
                                         The list contains unique conflict locations.

        Raises:
            IndexError: If the provided row or column index is out of bounds
                        for the board dimensions.
            ValueError: If the provided value is not within the valid Sudoku range (1-9).
        """
        if not (0 <= row < self._rows and 0 <= col < self._columns):
            raise IndexError(f"Row and column must be in the range 0–{self._rows - 1}.")
        if not (1 <= value <= 9):
            raise ValueError("Value must be in the range of 1-9")

        conflicts = []
        # On the same row
        for index, num in enumerate(self._board[row]):
            if (row, index) != (row, col) and num == value:
                conflicts.append((row, index))

        # On the same column
        for index, num in enumerate([r[col] for r in self._board]):
            if (index, col) != (row, col) and num == value:
                conflicts.append((index, col))

        # On the same 3x3 square
        y = (row // 3) * 3
        x = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                r = y + i # row index
                c = x + j # column index
                if (r, c) != (row, col) and self._board[r][c] == value:
                    conflicts.append((r, c))

        # Remove duplicates, order is not important here
        return list(set(conflicts))

    def get_board_copy(self) -> List[list[int, int]]:
        """
        Creates and returns a deep copy of the Sudoku board.

        This ensures that modifications to the returned board do not affect
        the original `SudokuBoard` object.

        Returns:
            List[list[int, int], ...]: A deep copy of the internal board representation.
        """
        return copy.deepcopy(self._board)

    def __str__(self) -> str:
        board_str = "Current Board\n"
        for i, row in enumerate(self._board):
            if i % 3 == 0:
                board_str += "+----------+---------+--------+\n"
            row_str = "|"
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "|"
                row_str += f" {val if val != 0 else ' '} "
            row_str += "|\n"
            board_str += row_str
        board_str += "+----------+---------+--------+\n"

        # For the Solved Board
        board_str += "\n\nSolved Board\n"
        for i, row in enumerate(self._solved_board):
            if i % 3 == 0:
                board_str += "+----------+---------+--------+\n"
            row_str = "|"
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "|"
                row_str += f" {val if val != 0 else ' '} "
            row_str += "|\n"
            board_str += row_str
        board_str += "+----------+---------+--------+\n"
        return board_str
            



if __name__ == "__main__":
    # Partially filled valid board (with zeros)
    partial_board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    # Fully solved valid board
    solved_board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]

    # Unsolvable board (contradiction)
    unrelated_board = [
        [0, 0, 3, 4, 5, 0, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 0, 0, 2, 3, 4, 5, 0],
        [2, 3, 0, 0, 6, 0, 8, 0, 0],
        [5, 0, 0, 8, 0, 0, 0, 3, 0],
        [8, 9, 0, 2, 3, 1, 0, 6, 0],
        [3, 1, 2, 6, 0, 5, 9, 7, 8],
        [6, 0, 0, 0, 7, 8, 3, 1, 0],
        [9, 7, 8, 3, 1, 2, 0, 0, 5],
    ]
    board = SudokuBoard(partial_board, solved_board, 0)
    print(str(board))