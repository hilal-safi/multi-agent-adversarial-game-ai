""" ui.py
    - This file contains the UIBuilder class that is responsible for drawing the game board and pieces
    - The class has methods to draw the background, board, and pieces
    - The class uses the pygame library to draw the UI
    - The class has methods to animate the dropping of pieces
    - The class has methods to draw the inner shadow and smooth circle 
    - The class has methods to update the display
    - The class has methods to handle the UI events
"""
import pygame
from typing import Tuple
from game.board import Board

try:
    import pygame.gfxdraw
    gfxdraw_available = True
except ImportError:
    gfxdraw_available = False

def draw_smooth_circle(screen: pygame.Surface, posx: int, posy: int, radius: int, color: Tuple[int, int, int]) -> None:
    if gfxdraw_available:
        pygame.gfxdraw.filled_circle(screen, posx, posy, radius, color)
        pygame.gfxdraw.aacircle(screen, posx, posy, radius, color)
    else:
        pygame.draw.circle(screen, color, (posx, posy), radius)

def draw_inner_shadow_circle(
    screen: pygame.Surface,
    posx: int,
    posy: int,
    radius: int,
    offset: Tuple[int, int]
):
    circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(circle_surf, (50,50,50, 100), (radius, radius), radius)

    pygame.draw.circle(circle_surf, (0, 0, 0, 0), (radius + offset[0], radius + offset[1]), radius)
    
    screen.blit(circle_surf, (posx - radius, posy - radius))

class UIBuilder:
    def __init__(
        self,
        board: Board,
        instant_animations = False,
        circle_size = 100,
        margin = 8,
        padding = 10,
        border_thickness = 4,
        shadow_thickness = 4,
        board_color = (30, 98, 243),
        empty_color = (0, 0, 0),
        background_color = (40, 40, 100),
        player_one_color = (205, 26, 48),
        player_two_color = (253, 197, 0),
        border_color = (47, 112, 252),
    ):
        self.board = board
        self.circle_size = circle_size
        self.margin = margin
        self.padding = padding 
        self.board_color = board_color
        self.empty_color = empty_color
        self.player_one_color = player_one_color
        self.player_two_color = player_two_color
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.shadow_thickness = shadow_thickness
        self.background_color = background_color
        self.instant_animations = instant_animations

        self.rows = board.rows
        self.columns = board.columns
        self.board_width = self.columns * self.circle_size
        self.board_height = (self.rows + 1) * self.circle_size

        self.width = self.board_width + 2 * self.padding
        self.height = self.board_height + 2 * self.padding

        self.size = (self.width, self.height)
        self.radius = int(self.circle_size / 2 - self.margin)

    def update_display(self):
        pygame.display.update()

    def draw_background(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.background_color, (0, 0, self.width, self.height))

    def draw_top_background(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.background_color, (0, 0, self.width, self.circle_size))

    def draw_top_piece(self, screen: pygame.Surface, posx: int, player: int) -> None:
        color = self.player_one_color if player == 1 else self.player_two_color
        draw_smooth_circle(screen, posx, int(self.circle_size / 2), self.radius, color)

    def draw_board(self, screen: pygame.Surface) -> None:
        board_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        board_surf.fill(self.board_color)
        
        for c in range(self.columns):
            for r in range(self.rows):
                circle_rect = pygame.Rect(
                    c * self.circle_size + self.padding,
                    (r + 1) * self.circle_size + self.padding,
                    self.circle_size,
                    self.circle_size,
                )
                pygame.draw.rect(board_surf, self.board_color, circle_rect)
                
                piece = self.board.grid[r][c]
                posx = int(c * self.circle_size + self.circle_size / 2 + self.padding)
                posy = int((r + 1) * self.circle_size + self.circle_size / 2 + self.padding)

                shadow_color = (50, 50, 50)
                pygame.draw.rect(board_surf, (0, 0, 0, 0), (0, 0, self.width, self.circle_size))

                # - Outer shadow for hole
                pygame.draw.circle(board_surf, shadow_color, (posx + self.shadow_thickness, posy + self.shadow_thickness), self.radius + self.border_thickness)

                # - Border for hole
                pygame.draw.circle(board_surf, (47, 112, 252), (posx, posy), self.radius + self.border_thickness)

                if piece == 0:
                    # - Circle cut out (the hole)
                    pygame.draw.circle(board_surf, (0, 0, 0, 0), (posx, posy), self.radius)
                else:
                    # - Player piece on board
                    color = self.player_one_color if piece == 1 else self.player_two_color
                    pygame.draw.circle(board_surf, color, (posx, posy), self.radius)

                # - Inner shadow for hole
                draw_inner_shadow_circle(
                    board_surf,
                    posx,
                    posy,
                    self.radius,
                    (self.shadow_thickness - 1, self.shadow_thickness - 1)
                )
        
        screen.blit(board_surf, (0, 0))

    def animate_piece_drop(self, screen: pygame.Surface, col: int, piece: int, target_row: int, gravity = 3.0, damping = 0.2, bounce_threshold = 2.0) -> None:
        if (self.instant_animations):
          # - If instant animations are on, return early and skip the animation
          return

        clock = pygame.time.Clock()
        start_y = self.circle_size / 2
        final_y = (target_row + 1) * self.circle_size + self.circle_size / 2 + self.padding
        current_y = start_y
        velocity = 0.0
        posx = int(col * self.circle_size + self.circle_size / 2 + self.padding)
        color = self.player_one_color if piece == 1 else self.player_two_color

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            velocity += gravity
            current_y += velocity

            if current_y >= final_y:
                current_y = final_y
                velocity = -velocity * damping
                if abs(velocity) < bounce_threshold:
                    current_y = final_y
                    break

            self.draw_background(screen)
            self.draw_top_background(screen)
            draw_smooth_circle(screen, posx, int(current_y), self.radius, color)
            self.draw_board(screen)
            self.update_display()
            clock.tick(60)

