from game.board import Board, check_win as board_check_win
# Key functions to implement:
def initialize_game():
    # Create empty 7x6 board, set player 1 as starting player
    return {
        'board': [[0] * 6 for _ in range(7)],
        'current_player': 1,
        'move_history': []
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
    board = state['board']
    # In each column, index 0 is the bottom.
    for row in range(6):
        if board[column][row] == 0:
            board[column][row] = state['current_player']
            # Record the move for later undo: (column, row)
            state['move_history'].append([column, row])
            # Switch current player: if 1 then become 2, and vice versa.
            state['current_player'] = 2 if state['current_player'] == 1 else 1
            return state
    # If no empty spot is found, the column is full.
    raise ValueError(f"Column {column} is full. Invalid move.")

def undo_move(state):
    if not state['move_history']:
        raise ValueError("No moves to undo.")
    # Get the last move (column, row)
    column, row = state['move_history'].pop()
    # Retrieve the player who made that move.
    removed_player = state['board'][column][row]
    # Remove the disc.
    state['board'][column][row] = 0
    # Revert the current player to the one who made the undone move.
    state['current_player'] = removed_player
    return state

    
def check_win(state):
    # Check for 4-in-a-row horizontally, vertically, and diagonally
    # Return winner (1 or 2) if found, else None
    if board_check_win(state, 1):
        return 1
    if board_check_win(state, 2):
        return 2
    return None
    
def is_draw(state):
    # Check if board is full with no winner
    return all(not state.is_valid_move(col) for col in range(state.columns)) and \
           not check_win(state, 1) and not check_win(state, 2)
    
def is_terminal(state):
    # Return True if game is won or drawn
    return check_win(state, state['move_history'][-1]) or is_draw(state)

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
                
        return 1  # Returns 1, 2, or 0 (draw)
    
state = initialize_game()
display_board(state)
make_move(state, 0)
display_board(state)
undo_move(state)
display_board(state)
make_move(state, 1)
display_board(state)
row, col = state['move_history'][-1]
print(row, col)
print(state['move_history'])
