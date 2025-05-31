import pygame
import math
import time
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
        self.button_hover_color = (70, 70, 200)
        self.inactive_color = (100, 100, 100)
        
        # Окно
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Poker")
        self.screen_width, self.screen_height = width, height
        
        # Шрифты
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        
        # Кнопки
        self.buttons = {
            'fold': {'rect': None, 'text': 'Fold', 'hover': False},
            'call': {'rect': None, 'text': 'Call', 'hover': False},
            'raise': {'rect': None, 'text': 'Raise', 'hover': False}
        }
        
        self._calculate_positions()
        self.game.start_new_hand()
        self.last_game_step_time = time.time()

    def _calculate_positions(self):
        """Пересчет позиций при изменении размера окна"""
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
        """Отрисовка покерного стола"""
        center = (self.screen_width//2, self.screen_height//2)
        table_radius = min(self.screen_width, self.screen_height) * 0.4
        pygame.draw.circle(self.screen, self.table_color, center, int(table_radius))
        
        # Рисуем логотип в центре
        title = self.title_font.render("POKER", True, self.text_color)
        title_rect = title.get_rect(center=center)
        self.screen.blit(title, title_rect)

    def _draw_community_cards(self, cards):
        """Отрисовка общих карт на столе"""
        if cards:
            card_spacing = 60
            total_width = (len(cards) - 1) * card_spacing
            start_x = self.screen_width//2 - total_width//2
            y = self.screen_height//2 - 30
            
            for i, card in enumerate(cards):
                # Создаем фон для карты
                card_bg = pygame.Rect(start_x + i*card_spacing - 25, y - 20, 50, 70)
                pygame.draw.rect(self.screen, (255, 255, 255), card_bg, border_radius=5)
                pygame.draw.rect(self.screen, (0, 0, 0), card_bg, 2, border_radius=5)
                
                # Рисуем текст карты
                text = self.font.render(str(card), True, (0, 0, 0))
                text_rect = text.get_rect(center=(start_x + i*card_spacing, y))
                self.screen.blit(text, text_rect)

    def _draw_players(self, game_state):
        """Отрисовка игроков и их информации"""
        for i, player in enumerate(game_state['players']):
            x, y = self.player_positions[i]
            
            # Цвет текста в зависимости от активности
            text_color = self.text_color if player['is_active'] else self.inactive_color
            
            # Карты игрока
            if player['is_bot']:
                cards_text = '?? ??'
            else:
                cards_text = ' '.join(str(c) for c in player['cards'])
            
            text = self.font.render(cards_text, True, text_color)
            text_rect = text.get_rect(center=(x, y))
            
            # Рамка вокруг карт игрока
            border_color = (200, 200, 100) if player['is_active'] else self.inactive_color
            pygame.draw.rect(self.screen, border_color, 
                           (text_rect.x-10, text_rect.y-5, 
                            text_rect.width+20, text_rect.height+10), 
                           2, border_radius=5)
            
            self.screen.blit(text, text_rect)
            
            # Статистика игрока
            info_text = f"${player['stack']} | Bet: ${player['current_bet']}"
            info = self.button_font.render(info_text, True, text_color)
            self.screen.blit(info, (x - info.get_width()//2, y + 30))
            
            # Пометка дилера
            if i == self.game.dealer_position:
                dealer_text = self.button_font.render("D", True, (255, 215, 0))
                self.screen.blit(dealer_text, (x - 40, y - 40))

    def _draw_buttons(self):
        """Отрисовка кнопок действий игрока"""
        if self.game.waiting_for_human_input:
            button_width = 120
            button_height = 50
            spacing = 20
            total_width = 3 * button_width + 2 * spacing
            start_x = self.screen_width//2 - total_width//2
            y = self.screen_height - 80
            
            for i, (action, data) in enumerate(self.buttons.items()):
                x = start_x + i*(button_width + spacing)
                rect = pygame.Rect(x, y, button_width, button_height)
                data['rect'] = rect
                
                # Цвет кнопки при наведении
                color = self.button_hover_color if data['hover'] else self.button_color
                
                # Рисуем кнопку
                pygame.draw.rect(self.screen, color, rect, border_radius=8)
                pygame.draw.rect(self.screen, self.text_color, rect, 2, border_radius=8)
                
                # Текст кнопки
                text = self.button_font.render(data['text'], True, self.text_color)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

    def _handle_hover(self, pos):
        """Обработка наведения на кнопки"""
        if self.game.waiting_for_human_input:
            for data in self.buttons.values():
                if data['rect']:
                    data['hover'] = data['rect'].collidepoint(pos)

    def _handle_click(self, pos):
        """Обработка кликов по кнопкам"""
        if self.game.waiting_for_human_input:
            for action, data in self.buttons.items():
                if data['rect'] and data['rect'].collidepoint(pos):
                    self.game.make_human_decision(action)
                    break

    def run(self):
        """Основной игровой цикл"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            current_time = time.time()
            
            # Обработка событий
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Обновляем размеры без перезагрузки игры
                    self.screen_width, self.screen_height = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (self.screen_width, self.screen_height), 
                        pygame.RESIZABLE
                    )
                    self._calculate_positions()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(mouse_pos)
            
            # Обновление состояния кнопок
            self._handle_hover(mouse_pos)
            
            # Обновление игры (с ограничением частоты)
            if (current_time - self.last_game_step_time > 0.1 and 
                not self.game.waiting_for_human_input and 
                not self.game.game_over):
                self.game.game_step()
                self.last_game_step_time = current_time
            
            # Получение текущего состояния игры
            game_state = self.game.get_game_state()
            
            # Отрисовка
            self.screen.fill(self.background_color)
            self._draw_table()
            self._draw_community_cards(game_state['community_cards'])
            self._draw_players(game_state)
            
            # Отображение банка
            pot_text = self.font.render(f"Pot: ${game_state['pot']}", True, self.text_color)
            self.screen.blit(pot_text, (20, 20))
            
            # Отображение текущей ставки
            bet_text = self.font.render(f"Current Bet: ${game_state['current_bet']}", True, self.text_color)
            self.screen.blit(bet_text, (20, 60))
            
            # Отображение текущего этапа игры
            stage_text = self.font.render(f"Stage: {game_state['stage']}", True, self.text_color)
            self.screen.blit(stage_text, (20, 100))
            
            # Отображение активного игрока
            active_player_text = self.font.render(
                f"Active: Player {self.game.current_player_index + 1}", 
                True, self.text_color
            )
            self.screen.blit(active_player_text, (20, 140))
            
            # Отрисовка кнопок
            self._draw_buttons()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    window = PokerWindow()
    window.run()
