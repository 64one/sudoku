import unittest
from unittest.mock import patch
import sys
import copy
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import sudoku_generator
from sudoku_validator import is_valid_board


class TestSudokuGenerator(unittest.TestCase):
    def setUp(self):
        # Create a valid complete Sudoku board for testing
        self.complete_board = [
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

    def test_generate_board_shape_and_empties(self):
        empties = 45
        empty_indicator = 0
        board, solved = sudoku_generator.generate(empties, empty_indicator = empty_indicator)
        self.assertEqual(len(board), 9)
        self.assertEqual(len(solved), 9)
        self.assertTrue(all(len(row) == 9 for row in board))
        self.assertTrue(all(len(row) == 9 for row in solved))

        # Count empties on generated board
        empty_count = sum(row.count(empty_indicator) for row in board)
        self.assertEqual(empty_count, empties)

    def test_generate_board_shape_and_empties_with_non_zero_empty_indicator(self):
        empties = 45
        empty_indicator = "empty"
        board, solved = sudoku_generator.generate(empties, empty_indicator = empty_indicator)
        self.assertEqual(len(board), 9)
        self.assertEqual(len(solved), 9)
        self.assertTrue(all(len(row) == 9 for row in board))
        self.assertTrue(all(len(row) == 9 for row in solved))

        # Count empties on generated board
        empty_count = sum(row.count(empty_indicator) for row in board)
        self.assertEqual(empty_count, empties)

    def test_generate_solved_board_is_valid(self):
        empty_indicator = -1
        board, solved = sudoku_generator.generate(30, empty_indicator = empty_indicator)
        self.assertTrue(is_valid_board(solved, empty_indicator))
        self.assertEqual(sum(row.count(empty_indicator) for row in solved), 0)

    def test_generate_raises_value_error_for_invalid_empties(self):
        with self.assertRaises(ValueError):
            sudoku_generator.generate(0)
        with self.assertRaises(ValueError):
            sudoku_generator.generate(-5)
        with self.assertRaises(ValueError):
            sudoku_generator.generate(82)

    def test_generate_randomness(self):
        board1, solved1 = sudoku_generator.generate(40)
        board2, solved2 = sudoku_generator.generate(40)
        self.assertNotEqual(board1[0], board2[0], "First rows should differ due to randomness")

    def test_generate_unique_solution(self):
        empties = 45
        empty_indicator = -1
        board, solved = sudoku_generator.generate(empties, unique=True, empty_indicator = empty_indicator)
        self.assertTrue(is_valid_board(solved, empty_indicator))
        empty_count = sum(row.count(empty_indicator) for row in board)
        self.assertEqual(empty_count, empties)

        # Ensure it has exactly one solution
        board_copy = [row.copy() for row in board]
        num_solutions = sudoku_generator.count_solutions(board_copy, empty_indicator = empty_indicator)
        self.assertEqual(num_solutions, 1, "Board should have a unique solution")

    def test_generate_unique_solution_custom_empty(self):
        """Test _create_unique_board with a custom empty cell indicator."""
        board = copy.deepcopy(self.complete_board)
        empty_indicator = 'X'
        sudoku_generator._create_unique_board(board, 20, empty_indicator)
        
        # Count empty cells
        empty_cells = sum(row.count(empty_indicator) for row in board)
        
        # Make sure we have created some empty cells
        self.assertGreater(empty_cells, 0)
        
        # Verify the board has a unique solution
        board_copy = copy.deepcopy(board)
        solutions = sudoku_generator.count_solutions(board_copy, limit=2, empty_indicator=empty_indicator)
        self.assertEqual(solutions, 1)

    @patch('random.randint')
    def test_create_unique_board_max_attempts(self, mock_randint):
        """Test that _create_unique_board handles max attempts gracefully."""
        # Mock random.randint to always return the same cell
        mock_randint.return_value = 0
        
        board = copy.deepcopy(self.complete_board)
        sudoku_generator._create_unique_board(board, 20)
        
        # Since we're always trying to remove the same cell,
        # we should hit max_attempts before reaching 20 empties
        empty_cells = sum(row.count(0) for row in board)
        self.assertLess(empty_cells, 20)

    def test_count_solutions_multiple(self):
        # Board with 27 blanks and has >= 4 distinct solutions
        board1 = [
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
        # This board has >= 10 distinct solutions
        board2 = [
            [0, 0, 3, 4, 5, 0, 0, 8, 9],
            [4, 5, 6, 0, 8, 9, 1, 2, 3],
            [0, 0, 0, 0, 2, 3, 4, 5, 0],
            [2, 3, 0, 0, 6, 0, 8, 0, 0],
            [5, 0, 0, 8, 0, 0, 0, 3, 0],
            [0, 9, 0, 2, 3, 1, 0, 6, 0],
            [3, 1, 2, 6, 0, 5, 9, 0, 8],
            [6, 0, 0, 0, 0, 8, 3, 1, 0],
            [9, 0, 0, 3, 1, 2, 0, 0, 5],
        ]
        solutions1 = sudoku_generator.count_solutions(board1)
        solutions2 = sudoku_generator.count_solutions(board2)
        self.assertGreater(solutions1, 1, "Board should have multiple solutions")
        self.assertGreater(solutions2, 1, "Board should have multiple solutions")

    def test_count_solutions_single(self):
        board, _ = sudoku_generator.generate(45, unique=True)
        solutions = sudoku_generator.count_solutions([row.copy() for row in board])
        self.assertEqual(solutions, 1, "Should have exactly one solution")

    def test_count_solutions_with_custom_empty_indicator(self):
        """Test count_solutions with a custom empty cell indicator."""
        board = copy.deepcopy(self.complete_board)
        # Replace one cell with 'X' as the empty indicator
        board[0][0] = 'X'
        solutions = sudoku_generator.count_solutions(board, empty_indicator='X')
        self.assertEqual(solutions, 1)

if __name__ == "__main__":
    unittest.main()
