""" board.py
 - This file contains the Board class and the functions to manipulate the board
    - The Board class has methods to reset the board, check if a move is valid, drop a piece, and check for a win
    - The functions check_win checks if a player has won the game
    - The Board class has the following attributes:
        - rows: the number of rows in the board
        - columns: the number of columns in the board
        - grid: a 2D list representing the board
    - The Board class has the following methods:
        - reset_board: resets the board to its initial state
        - is_valid_move: checks if a move is valid
        - get_next_open_row: gets the next open row in a column
        - drop_piece: drops a piece in the board
    - The functions check_win checks if a player has won the game
""" 
from dataclasses import dataclass, field
from typing import List, Optional

def create_empty_grid() -> List[List[int]]:
    grid: List[List[int]] = []
    for i in range(6):
        row: List[int] = []
        for j in range(7):
            row.append(0)
        grid.append(row)
    return grid

@dataclass
class Board:
    rows: int = 6
    columns: int = 7
    grid: List[List[int]] = field(default_factory=create_empty_grid)

    def reset_board(self):
        self.grid = create_empty_grid()

    def is_valid_move(self, col: int):
        return self.grid[0][col] == 0

    def get_next_open_row(self, col: int):
        for r in range(self.rows - 1, -1, -1):
            if self.grid[r][col] == 0:
                return r
        return None

    def drop_piece(self, row: int, col: int, piece: int):
        self.grid[row][col] = piece

    def to_string(self):
        # - I'm mapping 1 and 2 to A and B since Gemini was mixing the numbers up with the column numbers
        board_str = ""
        mapping = {1: "A", 2: "B"}
        for row in self.grid:
            board_str += "\n| " + " ".join(mapping.get(cell, str(cell)) for cell in row) + " |"
        column_numbers = "\n  " + " ".join(str(i + 1) for i in range(self.columns))
        board_str += column_numbers
        return board_str

def check_win(board: Board, piece: int) -> bool:
    # - horizontal
    for row_index in range(board.rows):
        for col_index in range(board.columns - 3):
            cell_1 = board.grid[row_index][col_index]
            cell_2 = board.grid[row_index][col_index + 1]
            cell_3 = board.grid[row_index][col_index + 2]
            cell_4 = board.grid[row_index][col_index + 3]

            if cell_1 == piece and cell_2 == piece and cell_3 == piece and cell_4 == piece:
                return True

    # - vertical
    for col_index in range(board.columns):
        for row_index in range(board.rows - 3):
            cell_1 = board.grid[row_index][col_index]
            cell_2 = board.grid[row_index + 1][col_index]
            cell_3 = board.grid[row_index + 2][col_index]
            cell_4 = board.grid[row_index + 3][col_index]

            if cell_1 == piece and cell_2 == piece and cell_3 == piece and cell_4 == piece:
                return True

    # - diagonal, south west to north-east
    for row_index in range(board.rows - 3):
        for col_index in range(board.columns - 3):
            cell_1 = board.grid[row_index][col_index]
            cell_2 = board.grid[row_index + 1][col_index + 1]
            cell_3 = board.grid[row_index + 2][col_index + 2]
            cell_4 = board.grid[row_index + 3][col_index + 3]

            if cell_1 == piece and cell_2 == piece and cell_3 == piece and cell_4 == piece:
                return True

    # - diagonal, north-west to south east
    for row_index in range(3, board.rows):
        for col_index in range(board.columns - 3):
            cell_1 = board.grid[row_index][col_index]
            cell_2 = board.grid[row_index - 1][col_index + 1]
            cell_3 = board.grid[row_index - 2][col_index + 2]
            cell_4 = board.grid[row_index - 3][col_index + 3]

            if cell_1 == piece and cell_2 == piece and cell_3 == piece and cell_4 == piece:
                return True

    return False