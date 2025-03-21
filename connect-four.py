# Key functions to implement:
def initialize_game():
    # Create empty 7x6 board, set player 1 as starting player
    
def get_valid_moves(state):
    # Return list of columns that aren't full
    
def make_move(state, column):
    # Place disc in the specified column at lowest available row
    # Update current player
    # Return new state
    
def check_win(state, last_move):
    # Check for 4-in-a-row horizontally, vertically, and diagonally
    # Return winner (1 or 2) if found, else None
    
def is_draw(state):
    # Check if board is full with no winner
    
def is_terminal(state):
    # Return True if game is won or drawn

def evaluate(state, player):
    # Assign score based on piece positions and potential winning moves
    # Higher scores favor player, lower scores favor opponent

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

def play_game(agent1, agent2, verbose=True):
    state = initialize_game()
    while not is_terminal(state):
        current_agent = agent1 if state['current_player'] == 1 else agent2
        move = current_agent.get_move(state)
        state = make_move(state, move)
        
        if verbose:
            display_board(state)
            
    return get_winner(state)  # Returns 1, 2, or 0 (draw)