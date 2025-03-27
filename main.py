import os
import sys
import math
import random
import pygame
from connect_four import initialize_board, MinimaxAgent
from game.board import Board, check_win
from game.ui import UIBuilder
from typing import Literal, Tuple, List

# - ------------------------------------------------------------------------------------------------------------------------------------------------------
# - The required package for Gemini is already specified in requirements.txt
# - The API is free, but if you want to avoid using Gemini (e.g. no API key), set the variable below to False. 

gemini_enabled = False

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

def show_play_again_button(screen: pygame.Surface) -> pygame.Rect:
    font = pygame.font.SysFont("monospace", 50)
    text_surface = font.render("Play Again", True, (255, 255, 255))
    padding_x, padding_y = 30, 20

    text_width, text_height = text_surface.get_size()
    button_width = text_width + padding_x * 2
    button_height = text_height + padding_y * 2

    button_x = (screen.get_width() - button_width) // 2
    button_y = (screen.get_height() - button_height) // 2

    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    button_surface.fill((0, 0, 0, 180)) 

    screen.blit(button_surface, (button_x, button_y))
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 3) 

    text_x = button_x + padding_x
    text_y = button_y + padding_y
    screen.blit(text_surface, (text_x, text_y))
    pygame.display.update()

    return button_rect

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

def pygame_game(mode: Literal["2player", "minimax", "alpha-beta", "gemini"] = "2player"):
    if mode == "gemini" and not gemini_enabled:
        raise Exception("Gemini is disabled but you are in gemini mode. Either enable gemini by setting gemini_enabled to True at the top of this file or change mode")

    if mode == "minimax":
        minimax_agent = MinimaxAgent(max_depth=5, use_alpha_beta=False)
    
    if mode == "alpha-beta":
        minimax_agent = MinimaxAgent(max_depth=5, use_alpha_beta=True)

    pygame.init()
    board = Board()

    # - Set instant_animations to True if you want to speed up the disk placements (In case you are simulating games quickly)
    ui = UIBuilder(board, instant_animations=False)

    screen = pygame.display.set_mode(ui.size)
    pygame.display.set_caption("Connect 4")
    game_over = False
    turn = 0

    ui.draw_background(screen)
    ui.draw_board(screen)
    ui.update_display()
    
    while not game_over:
        current_player = 1 if turn % 2 == 0 else 2

        # - Right now player 1 is controlled by the user, and the opponent varies based on mode

        if mode == "2player" or (mode != "2player" and current_player == 1):
            col = process_human_move(ui, board, screen, turn)
        elif mode == "gemini" and current_player == 2:
            # - Gemini 
            display_text(screen, f"Gemini Thinking...", (255, 255, 255))
            pygame.time.wait(500) 
            col = get_move_from_gemini(board)
        elif mode == "minimax" and current_player == 2:
            display_text(screen, f"Minimax Thinking...", (255, 255, 255))
            #col = get_random_column(board) # placeholder
            game_state = initialize_board(board, 2)
            col = minimax_agent.get_move(game_state)
            print(col)
        elif mode == "alpha-beta" and current_player == 2:
            display_text(screen,f"Alpha-Beta Thinking...", (255, 255, 255))
            game_state = initialize_board(board, 2)
            col = minimax_agent.get_move(game_state)
            print(col)
        else:
            raise Exception("No valid mode")

        row = board.get_next_open_row(col)
        if row is None:
          raise Exception("Could not find a row given a column")

        piece = 1 if turn % 2 == 0 else 2

        ui.animate_piece_drop(screen, col, piece, row)
        board.drop_piece(row, col, piece)

        if check_win(board, piece):
            ui.draw_top_background(screen)
            ui.draw_background(screen)
            ui.draw_board(screen)
            ui.update_display()
            display_text(screen, f"Player {piece} wins!", ui.player_one_color if piece == 1 else ui.player_two_color)
            game_over = True
            play_again_button = show_play_again_button(screen)
        else:
            ui.draw_top_background(screen)
            ui.draw_background(screen)
            ui.draw_board(screen)
            ui.update_display()

        turn += 1

        if game_over:
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.collidepoint(event.pos):
                        board.reset_board()
                        turn = 0
                        game_over = False
                        ui.draw_background(screen)
                        ui.draw_board(screen)
                        ui.update_display()
                        break

if __name__ == "__main__":
    # - Change mode here to change playing mode from the following: ["2player", "minimax", "alpha-beta", "gemini"]
    pygame_game("minimax")

