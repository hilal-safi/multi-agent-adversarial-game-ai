from game.board import Board, check_win as board_check_win
# Key functions to implement:
def initialize_game():
    # Create empty 7x6 board, set player 1 as starting player
    return {
        'board': [[0] * 6 for _ in range(7)],
        'current_player': 1
    }

def display_board(state):
    # FOR TESTING ONLY
    # Print board with player pieces
    # This is a helper function for testing
    print("1 2 3 4 5 6 7")
    for row in range(6):
        print(" ".join(str(state['board'][col][5-row]) for col in range(7)))
    pass
    
def get_valid_moves(state):
    # Return list of columns that aren't full
    return [col for col in range(state.columns) if state.is_valid_move(col)]
    
def make_move(state, column):
    # Place disc in the specified column at lowest available row
    # Update current player
    # Return new state
    return state
    
def check_win(state, last_move):
    # Check for 4-in-a-row horizontally, vertically, and diagonally
    # Return winner (1 or 2) if found, else None
    if not hasattr(last_move, 'row') or not hasattr(last_move, 'col'):
        # Fall back to full check if last_move doesn't have row/col
        if board_check_win(state, 1):
            return 1
        if board_check_win(state, 2):
            return 2
        return None
        
    row, col = last_move.row, last_move.col
    piece = state.grid[row][col]
    
    # Check horizontal
    for c in range(max(0, col-3), min(state.columns-3, col+1)):
        if (state.grid[row][c] == piece and
            state.grid[row][c+1] == piece and
            state.grid[row][c+2] == piece and
            state.grid[row][c+3] == piece):
            return piece
    
    # Check vertical
    for r in range(max(0, row-3), min(state.rows-3, row+1)):
        if (state.grid[r][col] == piece and
            state.grid[r+1][col] == piece and
            state.grid[r+2][col] == piece and
            state.grid[r+3][col] == piece):
            return piece
    
    # Check diagonal (top-left to bottom-right)
    for r, c in zip(range(row-3, row+1), range(col-3, col+1)):
        if r >= 0 and c >= 0 and r+3 < state.rows and c+3 < state.columns:
            if (state.grid[r][c] == piece and
                state.grid[r+1][c+1] == piece and
                state.grid[r+2][c+2] == piece and
                state.grid[r+3][c+3] == piece):
                return piece
    
    # Check diagonal (bottom-left to top-right)
    for r, c in zip(range(row+3, row-1, -1), range(col-3, col+1)):
        if r-3 >= 0 and c >= 0 and r < state.rows and c+3 < state.columns:
            if (state.grid[r][c] == piece and
                state.grid[r-1][c+1] == piece and
                state.grid[r-2][c+2] == piece and
                state.grid[r-3][c+3] == piece):
                return piece
    
    return None

def get_winner(state):
    return check_win(state, None)
    
def is_draw(state):
    # Check if board is full with no winner
    return all(not state.is_valid_move(col) for col in range(state.columns)) and \
           not check_win(state, 1) and not check_win(state, 2)
    
def is_terminal(state):
    # Return True if game is won or drawn
    return check_win(state, None) or is_draw(state)

def evaluate(state, player):
    # Assign score based on piece positions and potential winning moves
    # Higher scores favor player, lower scores favor opponent
    return 0

class ConnectFourAgent:
    def get_move(self, game_state):
        """Return the column (0-6) to place the next disc"""
        pass

class MinimaxAgent(ConnectFourAgent):
    def __init__(self, max_depth=5, use_alpha_beta=True):
        self.max_depth = max_depth
        self.use_alpha_beta = use_alpha_beta
        
    def get_move(self, game_state):
        # Find best move using minimax search
        # Use alpha-beta pruning if enabled
        pass

    def play_game(agent1, agent2, verbose=True):
        state = initialize_game()
        while not is_terminal(state):
            current_agent = agent1 if state['current_player'] == 1 else agent2
            move = current_agent.get_move(state)
            state = make_move(state, move)
            
            if verbose:
                display_board(state)
                
        return get_winner(state)  # Returns 1, 2, or 0 (draw)
    
state = initialize_game()
display_board(state)
#get_valid_moves(state)
is_terminal(state)
