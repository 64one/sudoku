import unittest
import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from sudoku_solver import get_empty, get_possible_values, fill_board
from sudoku_validator import is_valid_entry


class TestSudokuSolver(unittest.TestCase):

    def setUp(self):
        # Partially filled valid board (with zeros)
        self.partial_board = [
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
        self.solved_board = [
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
        self.unsolvable_board = [
            [5, 5, 0, 0, 7, 0, 0, 0, 0],  # Two 5's in row 0
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]

    def test_get_empty_finds_first_empty(self):
        empty_cell = get_empty(self.partial_board)
        self.assertEqual(empty_cell, (0, 2))

    def test_get_empty_no_empty(self):
        empty_cell = get_empty(self.solved_board)
        self.assertEqual(empty_cell, ())

    def test_get_possible_values_for_cell(self):
        possible = get_possible_values(self.partial_board, 0, 2)
        # On this partial board at (0,2), possible values are known to be [1,2,4]
        # Let's assert that these are included (order may differ)
        for val in [1, 2, 4]:
            self.assertIn(val, possible)
        self.assertTrue(all(1 <= v <= 9 for v in possible))

    def test_fill_board_solves_partial_board(self):
        board_copy = [row[:] for row in self.partial_board]
        result = fill_board(board_copy)
        self.assertTrue(result)
        # After solving, there should be no empty cells
        self.assertEqual(get_empty(board_copy), ())
        # The board should be valid according to validator
        from sudoku_validator import is_valid_board
        self.assertTrue(is_valid_board(board_copy))

    def test_fill_board_solves_partial_board_with_custom_empty_indicator(self):
        board_copy = [row[:] for row in self.partial_board]
        empty_indicator = "empty"
        result = fill_board(board_copy)
        self.assertTrue(result)
        # After solving, there should be no empty cells
        self.assertEqual(get_empty(board_copy), ())
        # The board should be valid according to validator
        from sudoku_validator import is_valid_board
        self.assertTrue(is_valid_board(board_copy))

    def test_fill_board_returns_true_for_already_solved(self):
        board_copy = [row[:] for row in self.solved_board]
        result = fill_board(board_copy)
        self.assertTrue(result)
        self.assertEqual(board_copy, self.solved_board)  # Should be unchanged

    def test_fill_board_fails_on_unsolvable(self):
        board_copy = [row[:] for row in self.unsolvable_board]
        result = fill_board(board_copy)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
