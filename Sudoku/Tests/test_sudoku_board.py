import unittest
import copy
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import sudoku_validator
import sudoku_generator
from sudoku_board import SudokuBoard


class TestSudokuBoard(unittest.TestCase):
    def setUp(self):
        # Create sample boards for testing
        self.empty_board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Valid unsolved board
        self.unsolved_board = [
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
        
        # Valid solved board matching the unsolved board
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
        
        # Almost solved board with just one empty square
        self.almost_solved_board = copy.deepcopy(self.solved_board)
        self.almost_solved_board[0][0] = 0

    def test_init_valid_boards(self):
        """Test initialization with valid boards"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        self.assertEqual(board.get_current_board(), self.unsolved_board)
        self.assertEqual(len(board.prefilled_squares), 30)  # Count of non-zero cells in unsolved_board
        self.assertEqual(len(board.player_fillable_squares), 51)  # Count of zero cells in unsolved_board
        self.assertEqual(len(board.edited_squares), 0)

    def test_init_invalid_dimensions(self):
        """Test initialization with invalid board dimensions"""
        invalid_board = [[0 for _ in range(8)] for _ in range(9)]  # Only 8 columns
        with self.assertRaises(IndexError):
            SudokuBoard(invalid_board, self.solved_board)

    def test_init_invalid_values(self):
        """Test initialization with invalid values in board"""
        invalid_board = copy.deepcopy(self.unsolved_board)
        invalid_board[0][0] = 10  # Valid values are 0-9
        with self.assertRaises(ValueError):
            SudokuBoard(invalid_board, self.solved_board)

    def test_init_unsolved_solved_mismatch(self):
        """Test initialization with unsolved and solved boards that don't match"""
        mismatched_unsolved = copy.deepcopy(self.unsolved_board)
        mismatched_unsolved[0][0] = 6  # Different from solved_board[0][0] which is 5
        with self.assertRaises(ValueError):
            SudokuBoard(mismatched_unsolved, self.solved_board)

    def test_init_invalid_solved_board(self):
        """Test initialization with an incomplete solved board"""
        incomplete_solved = copy.deepcopy(self.solved_board)
        incomplete_solved[0][0] = 0  # Should be fully solved
        with self.assertRaises(ValueError):
            SudokuBoard(self.unsolved_board, incomplete_solved)

    def test_is_valid_board(self):
        """Test is_valid_board method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        self.assertTrue(board.is_valid_board())
        
        # Test invalid board
        invalid = copy.deepcopy(self.unsolved_board)
        invalid[0][0] = invalid[0][2] = 3  # Duplicate in row
        self.assertFalse(board.is_valid_board(board=invalid))

        # Test with expected empties parameter
        self.assertTrue(board.is_valid_board(expected_empties=51))
        self.assertFalse(board.is_valid_board(expected_empties=50))

    def test_is_valid_entry(self):
        """Test is_valid_entry method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Test valid entry in empty cell
        self.assertTrue(board.is_valid_entry(0, 2, 4))  # This matches the solved board's value
        
        # Test invalid entry (conflicts with row)
        self.assertFalse(board.is_valid_entry(0, 2, 5))  # 5 already exists in row 0
        
        # Test invalid entry (conflicts with column)
        self.assertFalse(board.is_valid_entry(0, 2, 8))  # 8 already exists in column 2
        
        # Test invalid entry (conflicts with 3x3 grid)
        self.assertFalse(board.is_valid_entry(0, 2, 9))  # 9 already exists in top-left 3x3 grid
        
        # Test prefilled square (should reject any change)
        self.assertFalse(board.is_valid_entry(0, 0, 9))  # Cell [0,0] is prefilled with 5
        
        # Test out of bounds
        with self.assertRaises(IndexError):
            board.is_valid_entry(9, 0, 1)
        
        # Test invalid value
        with self.assertRaises(ValueError):
            board.is_valid_entry(0, 2, 10)

    def test_reset_board(self):
        """Test reset_board method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Make some changes
        board.set_value(0, 2, 4)
        board.set_value(1, 1, 7)
        
        # Reset and verify
        result = board.reset_board()
        self.assertEqual(result, self.unsolved_board)
        self.assertEqual(board.get_current_board(), self.unsolved_board)
        self.assertEqual(board.edited_squares, [])

    def test_update_to_solved(self):
        """Test update_to_solved method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Make some changes
        board.set_value(0, 2, 4)
        board.set_value(1, 1, 7)
        
        # Update to solved and verify
        board.update_to_solved()
        self.assertEqual(board.get_current_board(), self.solved_board)
        self.assertEqual(board.edited_squares, [])

    def test_total_empty_squares(self):
        """Test total_empty_squares method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Count empties in unsolved board
        self.assertEqual(board.total_empty_squares(), 51)
        
        # Count empties in solved board
        self.assertEqual(board.total_empty_squares(board=self.solved_board), 0)
        
        # Count empties in custom board
        self.assertEqual(board.total_empty_squares(board=self.almost_solved_board), 1)

    @patch('sudoku_generator.count_solutions')
    def test_has_one_solution(self, mock_count_solutions):
        """Test has_one_solution method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Test with one solution
        mock_count_solutions.return_value = 1
        self.assertTrue(board.has_one_solution())
        
        # Test with multiple solutions
        mock_count_solutions.return_value = 2
        self.assertFalse(board.has_one_solution())
        
        # Test with no solutions
        mock_count_solutions.return_value = 0
        self.assertFalse(board.has_one_solution())

    @patch('random.choice')
    def test_get_hint(self, mock_choice):
        """Test get_hint method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Set random.choice to return a specific empty square
        mock_choice.return_value = (0, 2)  # This is an empty square in unsolved_board
        
        # Get hint and verify
        hint = board.get_hint()
        self.assertEqual(hint, (4, 0, 2))  # Value from solved_board at [0,2] is 4
        
        # Test with full board
        full_board = SudokuBoard(self.solved_board, self.solved_board)
        self.assertEqual(full_board.get_hint(), (0, 0, 0))
        
        # Test when all empty squares have been edited
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        # Simulate all empty squares being edited
        board.edited_squares = list(board.player_fillable_squares)
        self.assertEqual(board.get_hint(), (0, 0, 0))

    def test_is_currently_empty(self):
        """Test is_currently_empty method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Test empty cell
        self.assertTrue(board.is_currently_empty(0, 2))
        
        # Test non-empty cell
        self.assertFalse(board.is_currently_empty(0, 0))
        
        # Test out of bounds
        with self.assertRaises(IndexError):
            board.is_currently_empty(9, 0)

    def test_get_value(self):
        """Test get_value method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Get value from filled cell
        self.assertEqual(board.get_value(0, 0), 5)
        
        # Get value from empty cell
        self.assertEqual(board.get_value(0, 2), 0)
        
        # Test out of bounds
        with self.assertRaises(IndexError):
            board.get_value(9, 0)

    def test_set_value(self):
        """Test set_value method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Set valid value in empty cell
        self.assertTrue(board.set_value(0, 2, 4))
        self.assertEqual(board.get_value(0, 2), 4)
        self.assertIn((0, 2), board.edited_squares)
        
        # Try to set invalid value (conflicts with row)
        self.assertFalse(board.set_value(0, 3, 5))  # 5 already exists in row 0
        
        # Try to overwrite prefilled cell
        self.assertFalse(board.set_value(0, 0, 9))  # Cell [0,0] is prefilled
        
        # Try to set out of range value
        with self.assertRaises(ValueError):
            board.set_value(0, 3, 10)
        
        # Try to set out of bounds
        with self.assertRaises(IndexError):
            board.set_value(9, 0, 1)
        
        # Test changing a value without adding duplicate to edited_squares
        board.set_value(0, 2, 6)  # Change from 4 to 6
        self.assertEqual(board.edited_squares.count((0, 2)), 1)  # Should be in list only once

    def test_set_empty(self):
        """Test set_empty method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Fill a cell then set it back to empty
        board.set_value(0, 2, 4)
        self.assertIn((0, 2), board.edited_squares)
        
        # Clear the cell
        self.assertTrue(board.set_empty(0, 2))
        self.assertEqual(board.get_value(0, 2), 0)
        self.assertNotIn((0, 2), board.edited_squares)
        
        # Try to clear prefilled cell
        self.assertFalse(board.set_empty(0, 0))
        
        # Try to clear already empty cell
        self.assertFalse(board.set_empty(0, 2))  # Now empty again
        
        # Try to clear out of bounds
        with self.assertRaises(IndexError):
            board.set_empty(9, 0)

    def test_get_by_value(self):
        """Test get_by_value method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Find all cells with value 5
        fives = board.get_by_value(5)
        expected_fives = ((0, 0), (1, 5), (7, 8))
        self.assertEqual(set(fives), set(expected_fives))
        
        # Cells (4, 0), (7, 3) in the unsolved board have value 4
        self.assertNotEqual(board.get_by_value(4), ())
        
        # Test invalid value
        with self.assertRaises(ValueError):
            board.get_by_value(0)  # 0 is empty indicator
        with self.assertRaises(ValueError):
            board.get_by_value(10)

    def test_find_conflicts(self):
        """Test find_conflicts method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Find conflicts for a new value
        conflicts = board.find_conflicts(1, 1, 5)  # 5 already exists in row 0
        self.assertEqual(len(conflicts), 2)
        self.assertIn((0, 0), conflicts)  # Cell [0,0] has value 5
        self.assertIn((1, 5), conflicts)
        
        # Test with no conflicts
        no_conflicts = board.find_conflicts(0, 2, 4)  # 4 is valid for this cell
        self.assertEqual(no_conflicts, [])
        
        # Test out of bounds
        with self.assertRaises(IndexError):
            board.find_conflicts(9, 0, 1)
        
        # Test invalid value
        with self.assertRaises(ValueError):
            board.find_conflicts(0, 2, 10)

    def test_get_board_copy(self):
        """Test get_board_copy method"""
        board = SudokuBoard(self.unsolved_board, self.solved_board)
        
        # Get a copy and verify it's a deep copy
        board_copy = board.get_board_copy()
        self.assertEqual(board_copy, board.get_current_board())
        
        # Modify the copy and verify original is unchanged
        board_copy[0][0] = 9
        self.assertNotEqual(board_copy, board.get_current_board())
        self.assertEqual(board.get_value(0, 0), 5)

    def test_empty_indicator(self):
        # Test with different empty indicator
        custom_empty = [
            [5, 3, -1, -1, 7, -1, -1, -1, -1],
            [6, -1, -1, 1, 9, 5, -1, -1, -1],
            [-1, 9, 8, -1, -1, -1, -1, 6, -1],
            [8, -1, -1, -1, 6, -1, -1, -1, 3],
            [4, -1, -1, 8, -1, 3, -1, -1, 1],
            [7, -1, -1, -1, 2, -1, -1, -1, 6],
            [-1, 6, -1, -1, -1, -1, 2, 8, -1],
            [-1, -1, -1, 4, 1, 9, -1, -1, 5],
            [-1, -1, -1, -1, 8, -1, -1, 7, 9]
        ]
        custom_solved = copy.deepcopy(self.solved_board)
        board = SudokuBoard(custom_empty, custom_solved, empty_indicator=-1)
        self.assertTrue(board.is_currently_empty(0, 2))
        self.assertEqual(board.total_empty_squares(), sum(1 for row in custom_empty for num in row if num == -1))

if __name__ == '__main__':
    unittest.main()
