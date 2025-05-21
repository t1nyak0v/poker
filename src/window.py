import pygame
import math
from game import PokerGame, GameStage

class PokerWindow:
    def __init__(self, width=800, height=600, num_players=6):
        pygame.init()
        self.game = PokerGame(num_players)
        self.num_players = num_players
        
        # Цвета
        self.background_color = (36, 32, 29)
        self.table_color = (6, 78, 45)
        self.text_color = (169, 205, 229)
        self.button_color = (50, 50, 150)
        
        # Окно
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Poker")
        self.screen_width, self.screen_height = width, height
        
        # Шрифты
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 20)
        
        # Кнопки
        self.buttons = {
            'fold': {'rect': None, 'text': 'Fold'},
            'call': {'rect': None, 'text': 'Call'},
            'raise': {'rect': None, 'text': 'Raise'}
        }
        
        self._calculate_positions()
        self.game.start_new_hand()

    def _calculate_positions(self):
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        radius = min(self.screen_width, self.screen_height) * 0.35
        
        self.player_positions = []
        angle_step = 360 / self.num_players
        start_angle = 270  # Начало снизу
        
        for i in range(self.num_players):
            angle = math.radians(start_angle + i * angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.player_positions.append((int(x), int(y)))

    def _draw_table(self):
        center = (self.screen_width//2, self.screen_height//2)
        table_radius = min(self.screen_width, self.screen_height) * 0.4
        pygame.draw.circle(self.screen, self.table_color, center, int(table_radius))

    def _draw_community_cards(self, cards):
        if cards:
            card_spacing = 60
            start_x = self.screen_width//2 - (len(cards)*card_spacing)//2
            y = self.screen_height//2 - 30
            
            for i, card in enumerate(cards):
                text = self.font.render(str(card), True, self.text_color)
                rect = text.get_rect(center=(start_x + i*card_spacing, y))
                self.screen.blit(text, rect)

    def _draw_players(self, game_state):
        for i, player in enumerate(game_state['players']):
            x, y = self.player_positions[i]
            
            # Карты игрока
            cards_text = ' '.join(str(c) for c in player['cards']) if not player['is_bot'] else '?? ??'
            text_color = self.text_color if player['is_active'] else (100, 100, 100)
            text = self.font.render(cards_text, True, text_color)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
            
            # Статистика игрока
            info_text = f"${player['stack']} | Bet: ${player['current_bet']}"
            info = self.button_font.render(info_text, True, text_color)
            self.screen.blit(info, (x - 50, y + 30))

    def _draw_buttons(self):
        if self.game.waiting_for_human_input:
            button_width = 100
            button_height = 40
            spacing = 20
            total_width = 3 * button_width + 2 * spacing
            start_x = self.screen_width//2 - total_width//2
            y = self.screen_height - 80
            
            for i, (action, data) in enumerate(self.buttons.items()):
                x = start_x + i*(button_width + spacing)
                rect = pygame.Rect(x, y, button_width, button_height)
                data['rect'] = rect
                
                pygame.draw.rect(self.screen, self.button_color, rect, border_radius=5)
                text = self.button_font.render(data['text'], True, self.text_color)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

    def _handle_click(self, pos):
        if self.game.waiting_for_human_input:
            for action, data in self.buttons.items():
                if data['rect'] and data['rect'].collidepoint(pos):
                    self.game.make_human_decision(action)
                    break

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            is_next = False
            self.screen.fill(self.background_color)
            self._draw_table()
            
            game_state = self.game.get_game_state()
            self._draw_community_cards(game_state['community_cards'])
            self._draw_players(game_state)
            
            # Отображение банка
            pot_text = self.font.render(f"Pot: ${game_state['pot']}", True, self.text_color)
            self.screen.blit(pot_text, (20, 20))
            
            # Отрисовка кнопок
            self._draw_buttons()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen_width, self.screen_height = event.size
                    self.screen = pygame.display.set_mode(
                        (self.screen_width, self.screen_height), 
                        pygame.RESIZABLE
                    )
                    self._calculate_positions()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        is_next = True
            
            # Обновление игры
            if not self.game.waiting_for_human_input and not self.game.game_over and is_next:
                self.game.game_step()
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    window = PokerWindow()
    window.run()
