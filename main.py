""" main.py
Connect 4 Game with Pygame and Minimax AI
- This file contains the main game loop and UI for the Connect 4 game
- The game can be played in different modes: 2-player, Minimax AI, Alpha-Beta Pruning AI, and Gemini AI
- The game uses the Pygame library for graphics and user input
- The game board is represented as a 2D list and the game logic is implemented in the Board class
- The game uses the Minimax algorithm with Alpha-Beta pruning to determine the best move for the AI
- The game has a UI that displays the game board, pieces, and player turns
"""
import os
import sys
import math
import random
import pygame
import time
import csv

# Global for tracking performance
LOG_RESULTS = True
CSV_FILENAME = "performance_log.csv"
 
def get_last_game_number(filename):
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        return 1
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header
        last_game = 0
        for row in reader:
            try:
                last_game = max(last_game, int(row[0]))
            except:
                continue
        return last_game + 1

from connect_four import initialize_board, MinimaxAgent
from game.board import Board, check_win
from game.ui import UIBuilder
from typing import Literal, Tuple, List

# - ------------------------------------------------------------------------------------------------------------------------------------------------------
# - The required package for Gemini is already specified in requirements.txt
# - The API is free, but if you want to avoid using Gemini (e.g. no API key), set the variable below to False. 

gemini_enabled = False
#gemini_enabled = True

# - To use Gemini's API, get a free API key and place it inside .env file like so: GEMINI_API_KEY=the_key
# -
# - Gemini's free API comes with rate limits, which means you can play a limit amount of moves per minute, but so far I've only hit it once
# - Currently, if you hit the quota, the code crashes since the 429 error isn't handled. Not sure how we want to handle it
# - Link to rate limits: https://ai.google.dev/gemini-api/docs/rate-limits#free-tier
# - Refer to game/gemini.py for which models are being used. A potential workaround is using other models gemini when we hit quota
# - 
# - As of now we're using Gemini as an opponent. The instructions mention we can also utilize it for testing and analysis
# - ------------------------------------------------------------------------------------------------------------------------------------------------------

if gemini_enabled:
    from game.gemini import get_move_from_gemini

def display_text(screen, text: str, color: Tuple[int, int, int]):
    font = pygame.font.SysFont("monospace", 60)
    label = font.render(
        text,
        True,
        color
    )
    screen.blit(label, (40, 10))
    pygame.display.update()

def show_play_again_buttons(screen: pygame.Surface) -> Tuple[pygame.Rect, pygame.Rect]:
    font = pygame.font.SysFont("monospace", 50)
    play_text = font.render("Play Again", True, (255, 255, 255))
    exit_text = font.render("Exit Game", True, (255, 255, 255))
    padding_x, padding_y = 30, 20

    play_width, play_height = play_text.get_size()
    exit_width, exit_height = exit_text.get_size()
    button_width = max(play_width, exit_width) + padding_x * 2
    button_height = play_height + padding_y * 2

    spacing = 50
    total_width = button_width * 2 + spacing
    start_x = (screen.get_width() - total_width) // 2
    button_y = (screen.get_height() - button_height) // 2

    play_rect = pygame.Rect(start_x, button_y, button_width, button_height)
    exit_rect = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)

    for rect, text_surface in [(play_rect, play_text), (exit_rect, exit_text)]:
        button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        button_surface.fill((0, 0, 0, 180))
        screen.blit(button_surface, (rect.x, rect.y))
        pygame.draw.rect(screen, (255, 255, 255), rect, 3)
        text_x = rect.x + padding_x
        text_y = rect.y + padding_y
        screen.blit(text_surface, (text_x, text_y))

    pygame.display.update()
    return play_rect, exit_rect

def get_random_column(board: Board) -> int:
    valid_moves = [c for c in range(board.columns) if board.is_valid_move(c)]
    if not valid_moves:
      raise Exception("No valid moves, cannot get random column")
    return random.choice(valid_moves)

last_mouse_x = None
def process_human_move(ui: UIBuilder, board: Board, screen: pygame.Surface, turn: int) -> int:
    global last_mouse_x
    current_player = 1 if turn % 2 == 0 else 2

    if last_mouse_x is not None:
        ui.draw_top_background(screen)
        ui.draw_top_piece(screen, last_mouse_x, current_player)
        ui.update_display()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            posx = event.pos[0]
            ui.draw_top_background(screen)
            ui.draw_top_piece(screen, posx, current_player)
            ui.update_display()
            last_mouse_x = posx
        if event.type == pygame.MOUSEBUTTONDOWN:
            posx = event.pos[0]
            col = int(math.floor(posx / ui.circle_size))
            if board.is_valid_move(col):
                return col

def pygame_game(mode: Literal["2player", "minimax", "alpha-beta", "gemini"] = "2player", game_number=1, simulate=False, auto_restart=False):
    pygame.init()
    winner = None
    game_start_time = time.time()
    
    if mode == "gemini" and not gemini_enabled:
        raise Exception("Gemini is disabled but you are in gemini mode. Either enable gemini by setting gemini_enabled to True at the top of this file or change mode")

    board = Board()
    if mode in ["minimax", "alpha-beta"]:
        minimax_agent = MinimaxAgent(max_depth=5, use_alpha_beta=(mode == "alpha-beta"))
    turn = 0
    fallback_used = False  # Reset fallback tracking for each new game

    # - Set instant_animations to True if you want to speed up the disk placements (In case you are simulating games quickly)
    ui = UIBuilder(board, instant_animations=False)

    screen = pygame.display.set_mode(ui.size)
    pygame.display.set_caption("Connect 4")
    game_over = False

    ui.draw_background(screen)
    ui.draw_board(screen)
    ui.update_display()
    
    while not game_over:
        current_player = 1 if turn % 2 == 0 else 2

        if current_player == 1:
            if simulate:
                col = get_random_column(board)
            else:
                col = process_human_move(ui, board, screen, turn)
        else:
            if mode == "gemini":
                display_text(screen, f"Gemini Thinking...", (255, 255, 255))
                pygame.time.wait(500) 
                start_time = time.time()
                col = get_move_from_gemini(board, game_number)
                duration = time.time() - start_time
                if col is None:
                    print("AI could not find a valid move. Choosing a random valid column.")
                    fallback_used = True
                    col = get_random_column(board)
                nodes = "N/A"
                if LOG_RESULTS:
                    with open(CSV_FILENAME, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([game_number, turn, "gemini", col, f"{duration:.4f}", nodes])
            elif mode in ["minimax", "alpha-beta"]:
                agent_label = "Minimax" if mode == "minimax" else "Alpha-Beta"
                display_text(screen, f"{agent_label} Thinking...", (255, 255, 255))
                game_state = initialize_board(board, 2)
                start_time = time.time()
                col, nodes = minimax_agent.get_move(game_state)
                if col is None:
                    print("AI could not find a valid move. Choosing a random valid column.")
                    fallback_used = True
                    col = get_random_column(board)
                duration = time.time() - start_time
                print(f"AI selected column {col} in {duration:.4f} seconds, nodes evaluated: {nodes}")
                if LOG_RESULTS:
                    with open(CSV_FILENAME, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([game_number, turn, mode, col, f"{duration:.4f}", nodes])
            else:
                raise Exception("No valid mode")

        row = board.get_next_open_row(col)
        if row is None:
          raise Exception("Could not find a row given a column")

        piece = 1 if turn % 2 == 0 else 2

        ui.animate_piece_drop(screen, col, piece, row)
        board.drop_piece(row, col, piece)

        if check_win(board, piece):
            winner = piece
            ui.draw_top_background(screen)
            ui.draw_background(screen)
            ui.draw_board(screen)
            ui.update_display()
            display_text(screen, f"Player {piece} wins!", ui.player_one_color if piece == 1 else ui.player_two_color)
            game_over = True
            play_again_button, exit_button = show_play_again_buttons(screen)

            if LOG_RESULTS and (simulate or mode in ["gemini", "minimax", "alpha-beta"]):
                game_duration = time.time() - game_start_time
                if winner == 1:
                    player_result = "Win"
                    agent_result = "Loss"
                elif winner == 2:
                    player_result = "Loss"
                    agent_result = "Win"
                else:
                    player_result = "Tie"
                    agent_result = "Tie"
                with open("game_result.csv", mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        game_number,
                        mode,
                        player_result,
                        agent_result,
                        1 if winner == 1 else 0,
                        1 if winner == 2 else 0,
                        f"{game_duration:.2f}",
                        1 if simulate else 0
                    ])
        else:
            ui.draw_top_background(screen)
            ui.draw_background(screen)
            ui.draw_board(screen)
            ui.update_display()

        turn += 1

        if fallback_used:
            display_text(screen, "Fallback: Random Move", (255, 255, 0))
            pygame.time.wait(1000)

        if game_over:
            fallback_used = False  # Reset fallback tracking for next game
            if simulate:
                pygame.quit()
            else:
                while True:
                    event = pygame.event.wait()
                    if event.type == pygame.QUIT or (event.type == pygame.MOUSEBUTTONDOWN and exit_button.collidepoint(event.pos)):
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and play_again_button.collidepoint(event.pos):
                        board.reset_board()
                        turn = 0
                        game_over = False
                        ui.draw_background(screen)
                        ui.draw_board(screen)
                        ui.update_display()
                        break

    if not simulate:
        return game_number
    elif simulate and auto_restart:
        return game_number + 1
    else:
        return game_number

def simulate_games(mode: Literal["minimax", "alpha-beta"], games: int = 10):
    wins = {1: 0, 2: 0}
    for i in range(games):
        board = Board()
        minimax_agent = MinimaxAgent(max_depth=5, use_alpha_beta=(mode == "alpha-beta"))
        turn = 0
        while True:
            current_player = 1 if turn % 2 == 0 else 2
            if current_player == 2:
                state = initialize_board(board, 2)
                col, _ = minimax_agent.get_move(state)
            else:
                col = get_random_column(board)
            row = board.get_next_open_row(col)
            if row is None:
                break
            board.drop_piece(row, col, current_player)
            if check_win(board, current_player):
                wins[current_player] += 1
                break
            turn += 1
    print(f"{mode} AI win rate over {games} games: {wins[2]} / {games}")

game_number = get_last_game_number(CSV_FILENAME)

if __name__ == "__main__":
    if LOG_RESULTS:
        if not os.path.exists(CSV_FILENAME):
            with open(CSV_FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Game", "Turn", "Agent", "Move", "Time(s)", "Nodes"])
        if not os.path.exists("game_result.csv"):
            with open("game_result.csv", mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["GameNum", "AgentUsed", "PlayerResult", "AgentResult", "PlayerScore", "AgentScore", "GameTime", "Simulated"])

    # -----------------------
    # Manual Testing Section
    # -----------------------

    # Uncomment to test manually with Minimax AI (player vs AI)
    #game_number = pygame_game("minimax", game_number=game_number)

    # Uncomment to test manually with Alpha-Beta AI (player vs AI)
    #game_number = pygame_game("alpha-beta", game_number=game_number)

    # Uncomment to test manually with Gemini AI (player vs AI)
    #game_number = pygame_game("gemini", game_number=game_number)

    # Uncomment to test 2-player mode (local multiplayer)
    # game_number = pygame_game("2player", game_number=game_number)

    # -------------------------
    # Simulated Testing Section
    # -------------------------

    # The number of games to simulate
    num_of_games = 2

    # Simulate multiple games using Minimax AI vs Random Player
    #for _ in range(num_of_games):
        #game_number = pygame_game("minimax", game_number=game_number, simulate=True, auto_restart=True)

    # Simulate multiple games using Alpha-Beta AI vs Random Player
    for _ in range(num_of_games):
        game_number = pygame_game("alpha-beta", game_number=game_number, simulate=True, auto_restart=True)

    # Simulate multiple games using Gemini AI vs Random Player
    # for _ in range(num_of_games):
    #     game_number = pygame_game("gemini", game_number=game_number, simulate=True, auto_restart=True)

    
