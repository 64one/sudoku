import unittest
import sys
import random
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from sudoku_validator import get_values_in_square, is_valid_entry,is_valid_board



class TestSudokuValidator(unittest.TestCase):

    def setUp(self):
        self.valid_board = [
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

    def test_valid_board(self):
        self.assertTrue(is_valid_board([row[:] for row in self.valid_board]))

    def test_invalid_row(self):
        board = [row[:] for row in self.valid_board]
        board[0][1] = 5  # Duplicate in row
        self.assertFalse(is_valid_board(board))

    def test_invalid_column(self):
        board = [row[:] for row in self.valid_board]
        board[1][0] = 5  # Duplicate in column
        self.assertFalse(is_valid_board(board))

    def test_invalid_square(self):
        board = [row[:] for row in self.valid_board]
        board[1][1] = 5  # Duplicate in 3x3 square
        self.assertFalse(is_valid_board(board))

    def test_unsolved_board(self):
        board = [row[:] for row in self.valid_board]
        board[0][0] = 0
        board[1][1] = 0
        self.assertTrue(is_valid_board(board))

    def test_unsolved_board_with_custom_empty_indicator(self):
        board = [row[:] for row in self.valid_board]
        empty_indicator = "x"
        for _ in range(20):
            row, col = random.randint(0, 8), random.randint(0, 8)
            board[row][col] = empty_indicator
        self.assertTrue(is_valid_board(board, empty_indicator))

    def test_non_9x9_board(self):
        with self.assertRaises(ValueError):
            is_valid_board([[1, 2], [3, 4]])

    def test_row_with_invalid_length(self):
        board = [row[:] for row in self.valid_board]
        board[0] = [1, 2, 3]
        with self.assertRaises(ValueError):
            is_valid_board(board)

    # --- Tests for get_values_in_square ---

    def test_get_square_top_left(self):
        expected = [5, 3, 4, 6, 7, 2, 1, 9, 8]
        result = get_values_in_square(self.valid_board, 1, 1)
        self.assertEqual(result, expected)

    def test_get_square_middle(self):
        expected = [7, 6, 1, 8, 5, 3, 9, 2, 4]
        result = get_values_in_square(self.valid_board, 4, 4)
        self.assertEqual(result, expected)

    def test_get_square_bottom_right(self):
        expected = [2, 8, 4, 6, 3, 5, 1, 7, 9]
        result = get_values_in_square(self.valid_board, 8, 8)
        self.assertEqual(result, expected)

    # --- Tests for is_valid_entry ---

    def test_valid_entry_true(self):
        board = [row[:] for row in self.valid_board]
        board[0][0] = 0  # Make empty temporarily
        self.assertTrue(is_valid_entry(board, 0, 0, 5))

    def test_valid_entry_false_in_row(self):
        board = [row[:] for row in self.valid_board]
        self.assertFalse(is_valid_entry(board, 0, 0, 3))  # 3 is already in row 0

    def test_valid_entry_false_in_column(self):
        board = [row[:] for row in self.valid_board]
        self.assertFalse(is_valid_entry(board, 0, 0, 6))  # 6 is in column 0

    def test_valid_entry_false_in_square(self):
        board = [row[:] for row in self.valid_board]
        self.assertFalse(is_valid_entry(board, 0, 0, 9))  # 9 is in top-left square

if __name__ == "__main__":
    unittest.main()
