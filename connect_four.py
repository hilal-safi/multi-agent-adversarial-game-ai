"""connect_four.py   
 - This file contains the Connect Four game logic and the Minimax agent
 - The game logic includes functions to initialize the board, make moves, check for wins, and evaluate the board
 - The Minimax agent uses the Minimax algorithm with Alpha-Beta pruning to determine the best move
 - The Minimax agent has a method to get the best move based on the current game state
 - The Minimax agent has a method to evaluate the board and assign scores to different game states
"""
from game.board import Board, check_win as board_check_win
import math, copy

def initialize_board(board=Board(), current_player=1):
    # Create a new Board instance instead of a raw list
    return {
        'board': board,
        'current_player': current_player
    }

def get_valid_moves(state):
    # Return list of columns that aren't full
    board = state['board']
    return [col for col in range(board.columns) if board.is_valid_move(col)]

def make_move(state, column):
    board = state['board']
    # Get the next open row for this column
    row = board.get_next_open_row(column)
    if row is None:
        raise ValueError(f"Column {column} is full. Invalid move.")
    
    # Drop the piece for the current player
    board.drop_piece(row, column, state['current_player'])
    # Switch current player
    state['current_player'] = 2 if state['current_player'] == 1 else 1
    return state

def check_win(state):
    # Check for 4-in-a-row for both players
    board = state['board']
    if board_check_win(board, 1):
        return 1
    if board_check_win(board, 2):
        return 2
    return None

def is_draw(state):
    # Check if board is full with no winner
    board = state['board']
    return all(not board.is_valid_move(col) for col in range(board.columns)) and \
           check_win(state) is None

def is_terminal(state):
    # Return True if game is won or drawn
    return check_win(state) is not None or is_draw(state)

def check_window(window, player=1, opponent=2):
    player_count = window.count(player)
    opponent_count = window.count(opponent)
    empty_count = window.count(0)

    # Scoring strategy
    if player_count == 4:
        return 100  # Winning
    elif player_count == 3 and empty_count == 1:
        return 5  # Potential win
    elif player_count == 2 and empty_count == 2:
        return 2  # creating line
    
    if opponent_count == 3 and empty_count == 1:
        return -4  # block opponent win
    
    return 0

def evaluate_board(state):
    board = state['board']
    total_score = 0
    player = state['current_player']
    opponent = 2 if player == 1 else 2

    # - horizontal
    for row_index in range(board.rows):
        for col_index in range(board.columns - 3):
            window = [board.grid[row_index][col_index + i] for i in range(4)]
            total_score += check_window(window, player, opponent)
            
    # - vertical
    for col_index in range(board.columns):
        for row_index in range(board.rows - 3):
            window = [board.grid[row_index + i][col_index] for i in range(4)]
            total_score += check_window(window, player, opponent)

    # - diagonal, south west to north-east
    for row_index in range(board.rows - 3):
        for col_index in range(board.columns - 3):
            window = [board.grid[row_index + i][col_index + i] for i in range(4)]
            total_score += check_window(window, player, opponent)

    # - diagonal, north-west to south east
    for row_index in range(3, board.rows):
        for col_index in range(board.columns - 3):
            window = [board.grid[row_index - i][col_index - i] for i in range(4)]
            total_score += check_window(window, player, opponent)

    return total_score

def value(state):
    if check_win(state) == 1:
        return math.inf
    if check_win(state) == 2:
        return -math.inf
    if is_draw(state):
        return 0
    
    return evaluate_board(state)

def result(state, move):
    new_state = copy.deepcopy(state)
    make_move(new_state, move)
    return new_state

def minimax(state, depth, maximizing_player, max_depth):
    # terminal state or max depth reached
    if is_terminal(state) or depth == max_depth:
        return value(state), None
    
    valid_moves = get_valid_moves(state)
    
    # Maximizing player (Player 1)
    if maximizing_player:
        best_score = -math.inf
        best_move = None
        for move in valid_moves:
            # Recursively explore moves
            score, _ = minimax(result(state, move), depth + 1, False, max_depth)
            if score > best_score:
                best_score = score
                best_move = move
        return best_score, best_move
    
    # Minimizing player (Player 2)
    else:
        best_score = math.inf
        best_move = None
        for move in valid_moves:
            # Recursively explore moves
            score, _ = minimax(result(state, move), depth + 1, True, max_depth)
            if score < best_score:
                best_score = score
                best_move = move
        return best_score, best_move
    
def minimax_alpha_beta(state, depth, maximizing_player, max_depth, alpha, beta):
    # Terminal state or max depth reached
    if is_terminal(state) or depth == max_depth:
        return value(state), None
    
    valid_moves = get_valid_moves(state)
    
    # Maximizing player (Player 1)
    if maximizing_player:
        best_score = -math.inf
        best_move = None
        for move in valid_moves:
            score, _ = minimax_alpha_beta(result(state, move), depth + 1, False, max_depth, alpha, beta)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break # Break cutoff
        return best_score, best_move
        
    #Minimizing player (Player 2)
    else:
        best_score = math.inf
        best_move = None
        for move in valid_moves:
            score, _ = minimax_alpha_beta(result(state, move), depth + 1, True, max_depth, alpha, beta)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break # Alpha cutoff
        return best_score, best_move

class ConnectFourAgent:
    def get_move(self, game_state):
        """Return the column (0-6) to place the next disc"""
        raise NotImplementedError("Subclasses must implement this method")

class MinimaxAgent(ConnectFourAgent):
    def __init__(self, max_depth=5, use_alpha_beta=False):
        self.max_depth = max_depth
        self.use_alpha_beta = use_alpha_beta
    
    def get_move(self, game_state):
        # Determine if maximizing or minimizing player
        maximizing_player = game_state['current_player'] == 1
        
        if (self.use_alpha_beta):
            # Minimax with Alpha Beta Pruning
            _, best_move = minimax_alpha_beta(game_state, 0, maximizing_player, self.max_depth)
        else:
            # Regular Minimax
            _, best_move = minimax(game_state, 0, maximizing_player, self.max_depth)

        # Debug output:
        print(f"Selected Move by AI: {best_move}")
        print(f"Current Board State:\n{game_state['board'].grid}")
        
        return best_move