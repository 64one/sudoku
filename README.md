# Sudoku Game

![sudoku_home](https://github.com/user-attachments/assets/5005fd00-d630-4008-8394-14a1fb2ed10e)

![sudoku_b](https://github.com/user-attachments/assets/011e99fc-4a54-4f76-82b9-a99baf1cf44b)

A feature-rich Sudoku game built with Python and PyQt that combines an elegant interface with powerful gameplay features.

## Features

- **Multiple Difficulty Levels**: Choose from Beginner, Intermediate, Advanced, and Expert modes
- **Intelligent Hints**: Get assistance when you're stuck with a limited number of hints
- **Auto-solve**: See the complete solution with one click
- **Conflict Detection**: Immediate feedback when a move violates Sudoku rules
- **Similar Value Highlighting**: Cells with the same number are highlighted for better visibility
- **Game Timer**: Track your solving time
- **Keyboard Navigation**: Use arrow keys and number keys for faster gameplay

## Installation

### Prerequisites

- Python 3.7+
- PyQt6

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/64one/sudoku.git
   ```

2. Navigate to the project directory:
   ```bash
   cd sudoku
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the game:
   ```bash
   python sudoku.py
   ```

## How to Play

1. **Select a Difficulty Level**: Choose from Beginner, Intermediate, Advanced, or Expert
2. **Fill in the Grid**: Click on a cell and enter a number (1-9)
3. **Navigation**:
   - Use mouse clicks to select cells
   - Use arrow keys to move between cells
   - Press numbers 1-9 to enter values
   - Press Delete or Backspace to clear a cell

## Controls

- **New Game**: Start a fresh game with the current difficulty level
- **Reset**: Clear all player entries while keeping the original puzzle
- **Undo**: Remove your most recent entry
- **Erase**: Clear the selected cell
- **Hint**: Get help on a cell (limited to 3 hints per game)
- **Solve**: View the complete solution

## Game Interface

- **Blue Numbers**: Player entries
- **Black Numbers**: Pre-filled puzzle numbers
- **Green Numbers**: Hint numbers
- **Red Highlighting**: Indicates rule conflicts
- **Gray Highlighting**: Shows all cells with the same value as the selected cell

## Technical Details

The game features:

- Optimized Sudoku generation algorithms
- Multi-threaded hint generation to prevent UI freezing
- Reliable puzzle validation to ensure solvability
- Clean, responsive UI design
- Keyboard shortcuts for improved user experience

## Development

### Project Structure

```
sudoku/
├── sudoku.py              # Application entry point
├── sudoku_generator.py    # Creates valid Sudoku puzzles
├── sudoku_validator.py    # Validates boards and entries
├── sudoku_solver.py       # Solves sudoku boards
├── sudoku_board.py        # Board logic and validation
├── Files/
│   └── sudoku.ui          # PyQt UI definition file
├── Tests/
│   └── test_sudoku_generator.py
│   └── test_sudoku_validator.py
│   └── test_sudoku_solver.py
│   └── test_sudoku_board.py
└── README.md              # This file
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License - see the LICENSE.md file for details.

## Acknowledgments

- The PyQt team for the excellent GUI framework
- Sudoku algorithm resources and communities
- All contributors and testers

---

Created by [64one](https://github.com/64one) • [Report Bug](https://github.com/64one/sudoku/issues)
