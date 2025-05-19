'''
black - (36, 32, 29)
green - (6, 78, 45)
blue - (169, 205, 229)
'''

import pygame
import math

class Window:
    def __init__(self, width=800, height=600, num_players=6):
        pygame.init()
        
        self.screen_width = width
        self.screen_height = height
        self.num_players = num_players
        self.margin_percent = 0.1 # percentage indentation from the screen edge

        self.background_color = (36, 32, 29)
        self.table_color = (6, 78, 45)
        self.text_color = (169, 205, 229)
        
        # Creating resizable window
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Poker")
        
        self.positions = self._calculate_positions()
        self.players_cards = [""] * self.num_players
        self.table_radius = (min(self.screen_width, self.screen_height) // 2) * (1 - 2 * self.margin_percent)

        self.font_size = 28
        self.font = pygame.font.SysFont('Arial', self.font_size, bold=True)

    """Calculating x & y for each player to draw card position"""
    def _calculate_positions(self):
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        half_size = min(self.screen_width, self.screen_height) // 2
        self.table_radius = half_size * (1 - 2 * self.margin_percent)
        
        positions = []
        angle_step = 360 / self.num_players
        start_angle = 270
        
        for i in range(self.num_players):
            angle_deg = start_angle + angle_step * i
            angle_rad = math.radians(angle_deg)
            x = center_x + self.table_radius * math.cos(angle_rad)
            y = center_y - self.table_radius * math.sin(angle_rad)
            positions.append((int(x), int(y)))
            
        return positions

    def update_players_cards(self, new_cards):
        if len(new_cards) == self.num_players:
            self.players_cards = new_cards
        else:
            print(f"Error: received {len(new_cards)} of cards instead of {self.num_players}")

    def _draw_background(self):
        self.screen.fill(self.background_color)

        if self.table_radius > 0:
            center = (self.screen_width//2, self.screen_height//2)
            pygame.draw.circle(
                    self.screen,
                    self.table_color,
                    center,
                    self.table_radius - self.font_size
            )


    def _draw_players_cards(self):
        for i, (x, y) in enumerate(self.positions):
            text_surface = self.font.render(self.players_cards[i], True, self.text_color)
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)


    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Обработка изменения размера окна
                    self.screen_width, self.screen_height = event.size
                    self.positions = self._calculate_positions()
            
            self._draw_background()
            self._draw_players_cards()
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    game_window = Window()
    test_cards = [
        "Dealer", "Unknown", "Unknown",
        "5♥ 3♣", "Unknown", "Unknown"
    ]
    game_window.update_players_cards(test_cards)
