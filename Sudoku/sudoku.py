from PyQt6.QtWidgets import (
    QApplication, QMainWindow, 
    QMessageBox, QPushButton
)
from PyQt6.QtCore import (
    QThread, QTimer, QElapsedTimer,
    pyqtSignal, Qt, QEvent, QObject
)
from PyQt6.QtGui import QFont
from PyQt6 import uic

import copy
import random
from pathlib import Path

import resources
import sudoku_generator
import sudoku_validator
import sudoku_solver
from sudoku_board import SudokuBoard


class ElapsedTimeCounter(QObject):
    """
    A QObject that tracks elapsed time and emits a signal periodically.

    This class uses a QElapsedTimer to measure the time passed since it was started
    and a QTimer to emit a signal containing the elapsed time at a fixed interval.
    It's designed to provide smooth updates of the elapsed time in seconds.

    Signals:
        time_difference (float): Emitted periodically with the elapsed time in seconds.
    """
    time_difference = pyqtSignal(float)

    def __init__(self):
        """
        Initializes the ElapsedTimeCounter.

        Sets up a QElapsedTimer to start measuring time immediately and a QTimer
        to trigger the emission of the elapsed time signal at a 100 millisecond interval.
        """
        super().__init__()
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._emit_elapsed_time)
        # Emit signal every 100 milliseconds, makes timer update smoothly
        self.timer.start(100)

    def _emit_elapsed_time(self):
        """
        Internal method called by the QTimer to emit the elapsed time signal.

        Calculates the elapsed time in milliseconds using the QElapsedTimer,
        converts it to seconds, and emits the 'time_difference' signal with this value.
        """
        elapsed_ms = self.elapsed_timer.elapsed()
        self.time_difference.emit(elapsed_ms / 1000.0)  # Convert to seconds

    def stop(self):
        """
        Stops the QElapsedTimer and QTimer, effectively pausing the emission 
        of the elapsed time signal and the track of the elapsed time.
        """
        self.timer.stop()
        self.elapsed_timer.stop()


class ShowHint(QThread):
    """
    A QThread that finds a valid hint for the current Sudoku board and emits a signal
    with the hint's value and position.

    This class performs the hint finding operation in a separate thread to prevent
    blocking the main GUI thread, ensuring a responsive user interface. It attempts
    to solve a copy of the board and, if successful, provides the value of one of the
    originally empty cells as a hint.

    Signals:
        hint_signal (int, int, int): Emitted with the hint's value (int), row index (int),
                                     and column index (int). If no hint can be found
                                     (e.g., no empty cells or unsolvable board), it emits
                                     (0, 0, 0).
    """
    hint_signal = pyqtSignal(int, int, int)
    def __init__(self, board: list[list[int]], empty_indicator: int|str):
        """
        Initializes the ShowHint thread.

        Args:
            board (list[list[int]]): A copy of the current Sudoku board.
            empty_indicator (int | str): The value representing an empty cell on the board.
        """
        super().__init__()
        self.board = board
        self.empty_indicator = empty_indicator

    def run(self):
        """
        Executes the hint finding logic in the thread.

        It first identifies all empty cells on the provided board. If there are no empty
        cells, it emits a signal indicating no hint. Otherwise, it randomly selects an
        empty cell and attempts to solve the board. If a solution is found, the value
        of the selected empty cell in the solved board is emitted as a hint along with
        its row and column.
        """
        got_hint = False

        # Find all empty (unfilled) cells
        empty_cells = [
            (i, j)
            for i in range(9)
            for j in range(9)
            if self.board[i][j] == self.empty_indicator
        ]
        if not empty_cells:
            self.hint_signal.emit(0, 0, 0) # No empty cells, no hint
            self.quit()
            return

        # Randomly select one
        row, col = random.choice(empty_cells)
        board_copy = [row[:] for row in self.board] # Work on a copy to avoid modifying the original
        if sudoku_solver.fill_board(board_copy, self.empty_indicator):
            value = board_copy[row][col]
            self.hint_signal.emit(value, row, col)

        self.quit()


class MainWindow(QMainWindow):
    """Creates the GUI.
    
    This class initializes and manages the Sudoku game GUI, including the game board, 
    user interactions, timer functionality, and game state management.
    """
    def __init__(self):
        """Initializes the Sudoku game GUI and sets up the initial state."""
        super().__init__()
        parent_path = Path(__file__).parent
        uic.loadUi(parent_path.joinpath("Files", "sudoku.ui"), self)
        
        # Cell buttons are named as "b[row][col]" e.g b03 is in row=0 and col=3
        # "b00", "b01", ..., "b88"
        # Sudoku is 9x9 grid, therefore wehave 9 rows and 9 cols with numbers 0 to 8
        self.cell_buttons = [
            [getattr(self, f"b{row}{col}") for col in range(9)] # A sublist for each row
            for row in range(9)
        ]

        # Highlight styles
        self.player_added_style = """
            QPushButton {
                background-color: white;
                color: rgb(33, 150, 243);
            }
            QPushButton:checked {
                background-color: white;
                color: rgb(33, 150, 243);
                font-weight: bold;
                border: 2px solid #585858;
                border-radius: 3px;
            }
        """
        self.prefilled_style = """
            QPushButton {
                background: #fff;
                color: #585858;
                font-weight: bold;
            }
        """
        self.conflict_highlight = """
            QPushButton {
                background-color: red;
                color: white;
                border: 1px solid #585858;
            }
        """
        self.hint_highlight = """
            QPushButton {
                background-color: rgb(0, 170, 0);
                color: white;
            }
        """
        self.same_value_highlight = """
            QPushButton {
                background-color: #bababa;
                color: black;
            }
            QPushButton:checked {
                background-color: #bababa;
                color: white;
                font-weight: bold;
                border: 2px solid black;
                border-radius: 3px;
            }
        """

        self.sudoku_board = None
        self.empty_indicator = 0
        self.level = 0
        self.game_playing = False
        self.getting_a_hint = False
        self.checked_button = None
        self.set_signals()
        self.reset_attributes()
        self.stackedWidget.setCurrentIndex(0)

    def closeEvent(self, event:QEvent) -> None:
        """Handles the window close event.
        
        Prompts the user for confirmation before closing if a game is in progress,
        and properly cleans up resources such as timers and threads.
        
        Args:
            event: The close event triggered when the user attempts to close the window.
        """
        if self.game_playing:
            reply = QMessageBox.question(
                self,
                "Exit Game",
                "Are you sure you want to exit the game?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        self.stop_timer()
        if hasattr(self, "hinter_thread") and self.hinter_thread.isRunning():
            self.hinter_thread.quit()
            self.hinter_thread.wait()

        event.accept()

    def keyPressEvent(self, event:QEvent) -> None:
        """Handles keyboard input events.
        
        Processes key presses for game actions: numbers 1-9 to input values,
        delete/backspace to erase values, and arrow keys for navigation.
        
        Args:
            event: The key press event containing the key that was pressed.
        """
        if event.key() in (
            Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
            Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
            Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9,
        ):
            self.update_button_text(event.text())

        elif event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.erase_selected_value()

        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            if self.checked_button:
                row, col = self.get_button_indexes(self.checked_button)
                if event.key() == Qt.Key.Key_Left:
                    next_col = max(col - 1, 0)
                else:
                    next_col = min(col + 1, 8)

                self.set_checked_button(self.cell_buttons[row][next_col])

        elif event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            if self.checked_button:
                row, col = self.get_button_indexes(self.checked_button)
                if event.key() == Qt.Key.Key_Up:
                    next_row = max(row -1, 0)
                else:
                    next_row = min(row + 1, 8)
                self.set_checked_button(self.cell_buttons[next_row][col])

    def set_signals(self) -> None:
        """Sets up all signal-slot connections for UI elements.
        
        Connects button clicks and other UI events to their corresponding handler methods.
        """
        # HomeScreen Buttons
        self.beginnerLevelButton.clicked.connect(lambda: self.set_level(0))
        self.intermediateLevelButton.clicked.connect(lambda: self.set_level(1))
        self.advancedLevelButton.clicked.connect(lambda: self.set_level(2))
        self.expertLevelButton.clicked.connect(lambda: self.set_level(3))

        # Game page
        self.levelComboBox.currentIndexChanged.connect(self.set_level)
        self.undoButton.clicked.connect(self.undo_last_entry)
        self.hintButton.clicked.connect(self.show_hint)
        self.newButton.clicked.connect(self.new_game)
        self.resetButton.clicked.connect(self.reset_game)
        self.eraseButton.clicked.connect(self.erase_selected_value)
        self.solveButton.clicked.connect(self.show_solution)

        # Board Buttons
        flattened_list = [but for but_row in self.cell_buttons for but in but_row]
        for cell_but in flattened_list:
            cell_but.clicked.connect(
                lambda checked, cell_but=cell_but: self.set_checked_button(cell_but)
            )
            cell_but.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def set_level(self, level:int) -> None:
        """Sets the difficulty level and starts a new game if needed.
        
        Args:
            level: An integer representing the difficulty level (0-3).
        """
        self.stackedWidget.setCurrentIndex(1)
        self.levelComboBox.setCurrentIndex(level)
        if self.level == level and self.game_playing:
            return
        # New level initiates a new game
        self.level = level
        self.new_game()

    def start_timer(self) -> None:
        """Initializes and starts the game timer.
        
        Creates a new ElapsedTimeCounter and connects its signal to update
        the time display.
        """
        self.update_time_lapsed(0)
        self.time_counter = ElapsedTimeCounter()
        self.time_counter.time_difference.connect(self.update_time_lapsed)

    def stop_timer(self, freeze_time:bool=False) -> None:
        """Stops the game timer.
        
        Args:
            freeze_time: If True, the current time is preserved on display.
                        If False, the timer is reset to 0.
        """
        try:
            self.time_counter.stop()
        except AttributeError:
            pass
        if not freeze_time:
            self.update_time_lapsed(0)

    def update_time_lapsed(self, time_lapsed: float|int) -> None:
        """Updates the displayed elapsed time label.
        
        Args:
            time_lapsed: The elapsed time in seconds to display.
        """
        time_lapsed = int(time_lapsed)
        hours, remainder = divmod(time_lapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            formatted_time = f"{minutes:02}:{seconds:02}"

        self.time_label.setText(f"Time: {formatted_time}")

    def reset_attributes(self) -> None:
        """Resets game state attributes and UI elements to their initial states."""
        if self.checked_button: # This is the selected cell
            self.checked_button.setChecked(False)
        self.checked_button = None
        self.update_hints(reset = True)
        self.reset_buttons_style()
        self.game_playing = False

    def reset_buttons_style(self) -> None:
        """Resets the styling of all cell buttons to their appropriate states.
        
        Applies the correct style to player-added numbers and prefilled numbers.
        """
        if self.sudoku_board == None: # In home page
            return

        # In game page
        for row, col in self.sudoku_board.player_fillable_squares:
            button = self.cell_buttons[row][col]
            button.setStyleSheet(self.player_added_style)

        for row, col in self.sudoku_board.prefilled_squares:
            button = self.cell_buttons[row][col]
            button.setStyleSheet(self.prefilled_style)
        
    def update_hints(self, reset:bool=False) -> None:
        """Updates the number of available hints.
        
        Args:
            reset: If True, resets hints to 3. If False, decrements the hint count.
        """
        self.hints = 3 if reset else self.hints - 1
        self.hints = max(0, self.hints)
        self.hint_label.setText(f"Hints: {self.hints}")

    def new_game(self) -> None:
        """Creates and starts a new Sudoku game.
        
        Generates a new Sudoku board based on the current difficulty level
        and initializes the game state.
        """
        self.stop_timer()
        self.reset_attributes()

        # Level difficulty is increased by increasing number
        # of empty squares
        level_ranges = {
            0: range(35, 41),
            1: range(41, 50),
            2: range(50, 59),
            3: range(59, 65),
        }
        empty_squares = random.choice(
            list(level_ranges.get(self.level, range(59, 65)))
        )

        # Generate a valid sudoku board
        while True:
            # Generating a unique puzzle with empty squares >= 50 takes a lot of time
            # and makes the GUI freeze.
            unique = True if self.level in (0, 1) else False
            board, solved_board = sudoku_generator.generate(
                empty_squares, 
                unique = unique,
                empty_indicator = self.empty_indicator
                )

            self.sudoku_board = SudokuBoard(
                board, 
                solved_board, 
                self.empty_indicator
                )

            if self.sudoku_board.is_valid_board(expected_empties = empty_squares):
                self.game_playing = True
                self.load_board()   
                self.start_timer()
                break

    def reset_game(self) -> None:
        """Resets the current game to its initial state.
        
        Clears player-added values while keeping the original puzzle intact.
        """
        self.sudoku_board.reset_board()
        self.reset_attributes()
        self.stop_timer()
        self.load_board()
        self.start_timer()
        self.game_playing = True

    def load_board(self) -> None:
        """Loads an initial board that will be filled, any number
        in the board shouldn't be changed.
        
        Populates the UI grid with the initial puzzle values from the board model.
        """
        for row in range(self.sudoku_board._rows):
            for col in range(self.sudoku_board._columns):
                value = self.sudoku_board.get_value(row, col)
                button = self.cell_buttons[row][col]
                if value == self.sudoku_board.empty_indicator:
                    button.setText("")
                else:
                    button.setText(str(value))

        self.reset_buttons_style()

    def set_checked_button(self, button:QPushButton) -> None:
        """Sets the currently selected cell button.
        
        Args:
            button: The button (cell) that was clicked or selected.
        """
        self.reset_buttons_style() # remove any highlights

        # Uncheck previously checked button
        if self.checked_button:
            self.checked_button.setChecked(False)
            self.checked_button = None

        button.setChecked(True)
        self.checked_button = button
        # Higlight all squares with similar number
        self.highlight_samilar_values(button)

    def get_button_indexes(self, button:QPushButton) -> tuple[int, int]:
        """Get the button indexes i.e row and col indexes on the board
        e.g button with name b21, will return row=2, col=1
        
        Args:
            button: The button whose position indexes are needed.
            
        Returns:
            A tuple containing (row, column) coordinates as integers.
        """
        button_name = button.objectName() # Returns the button name e.g b21
        numbers = button_name[-2:]
        row, col = int(numbers[0]), int(numbers[1])
        return row, col

    def update_button_text(self, num:int|str) -> None:
        """Updates the text/value of the currently selected button.
        
        Args:
            num: The number to set in the selected cell (1-9).
        """
        if not self.game_playing or self.getting_a_hint:
            return
        self.reset_buttons_style()
        if not self.checked_button:
            return

        # Don't change value for prefilled buttons
        row, col = self.get_button_indexes(self.checked_button)
        if (row, col) in self.sudoku_board.prefilled_squares:
            return

        # Validate user input
        num = int(num)
        if self.sudoku_board.set_value(row, col, num):
            self.checked_button.setText(str(num))
            self.is_game_completed()
            return # Prevents highlighting the cell as incorrect

        conflicts = self.sudoku_board.find_conflicts(row, col, num)
        if conflicts:
            for row, col in conflicts:
                button = self.cell_buttons[row][col]
                button.setStyleSheet(self.conflict_highlight)

    def is_game_completed(self) -> None:
        """Checks if the game is completed successfully.
        
        Verifies if all cells are filled and the solution is valid,
        then shows an appropriate message dialog.
        """
        if self.sudoku_board.total_empty_squares() > 0:
            return

        if self.sudoku_board.is_valid_board(expected_empties = 0):
            self.stop_timer(freeze_time=True)
            QMessageBox.information(
                self, 
                "Success", 
                "<b>Congratulations!</b><br>You've successfully solved the Sudoku puzzle.<br>"
            )
            self.game_playing = False

        else:
            # This should never be called as we always validate user input
            # but incase of bugs we have this
            QMessageBox.warning(
                self, 
                "Invalid", 
                "You've incorrectly filled the Sudoku puzzle."
            )

    def undo_last_entry(self) -> None:
        """Undoes the most recent player move by clearing the last edited cell."""
        if not self.game_playing or self.getting_a_hint:
            return

        if self.sudoku_board.edited_squares:
            row, col = self.sudoku_board.edited_squares[-1]
            last_edited_button = self.cell_buttons[row][col]
            if self.sudoku_board.set_empty(row, col):
                last_edited_button.setText("")
                self.reset_buttons_style() # remove any highlights

    def erase_selected_value(self) -> None:
        """Erases the value in the currently selected cell if it was added by the player."""
        if not self.game_playing or self.getting_a_hint:
            return

        if self.checked_button:
            row, col = self.get_button_indexes(self.checked_button)
            if (row, col) not in self.sudoku_board.edited_squares:
                return

            if self.sudoku_board.set_empty(row, col):
                self.checked_button.setText("")
                self.reset_buttons_style()

    def show_solution(self) -> None:
        """Shows the complete solution to the current puzzle.
        
        Fills in all cells with their correct values and ends the game. It
        uses a solved board that was generated during the start of the game.
        This maybe not be the only solution for levels above Intermediate.
        """
        if self.getting_a_hint:
            QMessageBox.warning(self, "Error", "Wait until a hint is generated!")
            return

        self.sudoku_board.update_to_solved()
        self.game_playing = False
        self.stop_timer()
        self.load_board()

    def show_hint(self) -> None:
        """Provides a hint by revealing one correct cell value.
        
        Uses a worker thread for generating hints, for boards with 
        more than one solution, to avoid UI freezing.
        """
        if not self.game_playing or self.getting_a_hint:
            return

        # Hint can only be shown when board isn't completed
        if self.sudoku_board.total_empty_squares() == 0:
            return

        if self.hints <= 0:
            QMessageBox.warning(
                self,
                "No Hints",
                """
                You have 0 hints left.<br>
                You can click the 'Solve' button to view the solution.
                """
            )
            return

        self.getting_a_hint = True

        if self.sudoku_board.has_one_solution():
            hint_value, row, col = self.sudoku_board.get_hint()
            self.insert_hint(hint_value, row, col)
            return

        self.hinter_thread = ShowHint(
            self.sudoku_board.get_board_copy(), 
            self.empty_indicator
        )
        self.hinter_thread.hint_signal.connect(self.insert_hint)
        self.hinter_thread.start()
        self.reset_buttons_style()
            
    def insert_hint(self, value:int, row:int, col:int) -> None:
        """Inserts a hint value into the specified cell.
        
        Args:
            value: The correct number to insert (1-9).
            row: The row index of the cell.
            col: The column index of the cell.
        """
        if value not in range(1, 10):
            QMessageBox.warning(
                self,
                "Error",
                "Unable to generate a hint, the board might be incorrectly filled."
            )
            return
        
        if self.sudoku_board.set_value(row, col, value):
            button = self.cell_buttons[row][col]
            button.setText(str(value))
            button.setStyleSheet(self.hint_highlight)
            self.update_hints()
            self.is_game_completed()
        else:
            QMessageBox.warning(self, "Error", "Unable to generate a hint")

        self.getting_a_hint = False

    def highlight_samilar_values(self, button:QPushButton) -> None:
        """Highlights all squares with similar value as the button.
        
        Args:
            button: The button whose value should be used for highlighting similar cells.
        """
        try:
            value = int(button.text())
            for row, col in self.sudoku_board.get_by_value(value):
                button = self.cell_buttons[row][col]
                button.setStyleSheet(self.same_value_highlight)

        except ValueError:
            return # No higlights needed for empty square


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    app.exec()