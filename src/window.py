'''
black - (36, 32, 29)
green - (6, 78, 45)
blue - (169, 205, 229)
'''
import pygame
import sys
import math
from typing import List, Tuple, Optional

# Инициализация Pygame
pygame.init()

# Начальные размеры окна
INIT_SCREEN_WIDTH = 1000
INIT_SCREEN_HEIGHT = 700
MIN_WIDTH = 800
MIN_HEIGHT = 600

# Константы
BACKGROUND_COLOR = (36, 32, 29)
TABLE_COLOR = (6, 78, 45)
PLAYER_TEXT_COLOR = (169, 205, 229)
CARD_COLOR = (255, 255, 255)
HIDDEN_CARD_COLOR = (50, 50, 150)
BUTTON_NORMAL_COLOR = (50, 50, 150)
BUTTON_HOVER_COLOR = (70, 70, 200)
BUTTON_PRESSED_COLOR = (30, 30, 120)
BUTTON_DISABLED_COLOR = (100, 100, 100)
PLAYER_ACTIVE_COLOR = (200, 200, 100)
PLAYER_INACTIVE_COLOR = (100, 100, 100)

# Относительные размеры элементов
TABLE_RADIUS_RATIO = 0.3
PLAYER_RADIUS_RATIO = 0.35
CARD_WIDTH_RATIO = 0.08
CARD_HEIGHT_RATIO = 0.13
BUTTON_WIDTH_RATIO = 0.1
BUTTON_HEIGHT_RATIO = 0.06
BUTTON_MARGIN_RATIO = 0.02
FONT_SIZE_RATIO = 0.025

class Card:
    """Класс для представления игральной карты"""
    def __init__(self, suit: str, rank: str):
        self.suit = suit  # Масть: ♥, ♦, ♣, ♠
        self.rank = rank  # Достоинство: 2-10, J, Q, K, A
        
    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"
    
    def render(self, surface: pygame.Surface, x: int, y: int, 
               card_width: int, card_height: int, visible: bool = True):
        """Отрисовка карты на поверхности"""
        rect = pygame.Rect(x, y, card_width, card_height)
        corner_radius = max(5, card_width // 10)
        
        if visible:
            # Видимая карта
            pygame.draw.rect(surface, CARD_COLOR, rect, 0, corner_radius)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2, corner_radius)
            
            font = pygame.font.SysFont('Arial', max(16, card_width // 4))
            text = font.render(str(self), True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        else:
            # Скрытая карта (рубашка)
            pygame.draw.rect(surface, HIDDEN_CARD_COLOR, rect, 0, corner_radius)
            pygame.draw.rect(surface, (200, 200, 200), rect, 2, corner_radius)
            
            # Рисуем узор на рубашке
            pattern_color = (70, 70, 180)
            pattern_radius = max(5, card_width // 8)
            pygame.draw.circle(surface, pattern_color, 
                              (x + card_width//2, y + card_height//3), 
                              pattern_radius)
            pygame.draw.circle(surface, pattern_color, 
                              (x + card_width//4, y + 2*card_height//3), 
                              pattern_radius)
            pygame.draw.circle(surface, pattern_color, 
                              (x + 3*card_width//4, y + 2*card_height//3), 
                              pattern_radius)


class Player:
    """Класс для представления игрока (человека или бота)"""
    def __init__(self, name: str, is_human: bool = False):
        self.name = name
        self.is_human = is_human
        self.cards: List[Card] = []
        self.position: Tuple[int, int] = (0, 0)
        self.folded = False
        self.stack = 1000  # Стартовый стек фишек
        self.current_bet = 40 
        self.is_active = False
        self.is_dealer = False
        self.border_pulse = 0
        
    def deal_card(self, card: Card):
        """Раздать карту игроку"""
        self.cards.append(card)
    
    def render(self, surface: pygame.Surface, card_width: int, card_height: int, font: pygame.font.Font):
        """Отрисовка игрока и его карт"""
        x, y = self.position
    
        # Цвет текста в зависимости от активности
        text_color = PLAYER_INACTIVE_COLOR
    
        # Рассчитываем смещение для карт
        offset = card_width
    
        if self.is_active:
            text_color = PLAYER_TEXT_COLOR

            pulse = abs(math.sin(self.border_pulse)) * 3 + 5

            # Рамка вокруг карт игрока (рисуем ПЕРЕД картами)
            border_rect = pygame.Rect(
                x - offset - 1, 
                y - 1, 
                card_width * 2 + 2, 
                card_height + 2
            )
            border_color = PLAYER_ACTIVE_COLOR if self.is_active else PLAYER_INACTIVE_COLOR
            pygame.draw.rect(surface, border_color, border_rect, int(pulse), 8)
            self.border_pulse += 0.5
    
        # Отображение карт (после обводки)
        for i, card in enumerate(self.cards):
            card_x = x - offset + i * card_width
            card_y = y
            visible = self.is_human or self.folded
            card.render(surface, card_x, card_y, card_width, card_height, visible)
        
        # Отображение имени игрока
        name_text = font.render(self.name, True, text_color)
        name_rect = name_text.get_rect(center=(x, y - 20))
        surface.blit(name_text, name_rect)
        
        # Отображение стека и ставки
        stack_text = font.render(f"S:${self.stack}", True, text_color)
        stack_rect = stack_text.get_rect(center=(x-(card_width//2)-6*FONT_SIZE_RATIO, y + card_height + 20))
        surface.blit(stack_text, stack_rect)
        
        # Отображение ставки
        if self.current_bet > 0:
            bet_text = font.render(f"B:${self.current_bet}", True, text_color)
            bet_rect = bet_text.get_rect(center=(x+(card_width//2), y + card_height + 20))
            surface.blit(bet_text, bet_rect)
        
        # Пометка дилера
        if self.is_dealer:
            dealer_text = font.render("D", True, (255, 215, 0))
            dealer_rect = dealer_text.get_rect(center=(x + (card_width//2), y - 20))
            surface.blit(dealer_text, dealer_rect)


class Button:
    """Класс для представления интерактивной кнопки"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.state = "normal"  # normal, hover, pressed, disabled
        self.colors = {
            "normal": BUTTON_NORMAL_COLOR,
            "hover": BUTTON_HOVER_COLOR,
            "pressed": BUTTON_PRESSED_COLOR,
            "disabled": BUTTON_DISABLED_COLOR
        }
        
    def update_position(self, x: int, y: int, width: int, height: int):
        """Обновление позиции и размера кнопки"""
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Отрисовка кнопки с учетом текущего состояния"""
        color = self.colors[self.state]
        corner_radius = max(5, self.rect.height // 10)
        pygame.draw.rect(surface, color, self.rect, 0, corner_radius)
        pygame.draw.rect(surface, PLAYER_TEXT_COLOR, self.rect, 2, corner_radius)

        text = font.render(self.text, True, PLAYER_TEXT_COLOR)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий кнопки, возвращает True если было нажатие"""
        if self.state == "disabled":
            return False
            
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.state = "hover"
            else:
                self.state = "normal"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.state = "pressed"
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.state = "hover"
                
        return False


class PokerGame:
    """Основной класс игры в покер"""
    def __init__(self, num_players: int = 4):
        # Создаем окно с поддержкой изменения размера
        self.screen = pygame.display.set_mode(
            (INIT_SCREEN_WIDTH, INIT_SCREEN_HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Poker Game")
        self.clock = pygame.time.Clock()
        
        # Текущие размеры экрана
        self.screen_width = INIT_SCREEN_WIDTH
        self.screen_height = INIT_SCREEN_HEIGHT
        
        # Рассчитываем размеры элементов
        self.calculate_sizes()
        
        # Шрифты
        self.font = pygame.font.SysFont('Arial', self.font_size)
        self.title_font = pygame.font.SysFont('Arial', int(self.font_size * 1.5), bold=True)
        
        # Создание игроков
        self.players: List[Player] = []
        self.create_players(num_players)
        self.players[1].is_dealer = True
        self.players[0].is_active = True
        
        # Создание кнопок
        self.buttons = self.create_buttons()
        
        # Тестовые карты
        self.deal_test_cards()
        
        # Расположение игроков вокруг стола
        self.arrange_players()
        
        # Общие карты
        self.community_cards = [
            Card("♥", "A"), 
            Card("♦", "K"), 
            Card("♣", "7"), 
            Card("♠", "2"), 
            Card("♥", "10")
        ]
        
        # Статистика игры
        self.pot = 500
        self.current_bet = 100
        
    def calculate_sizes(self):
        """Пересчет размеров элементов в зависимости от размера окна"""
        min_dimension = min(self.screen_width, self.screen_height)

        self.table_radius = int(min_dimension * TABLE_RADIUS_RATIO)
        self.card_width = int(min_dimension * CARD_WIDTH_RATIO)
        self.card_height = int(min_dimension * CARD_HEIGHT_RATIO)
        self.button_width = int(min_dimension * BUTTON_WIDTH_RATIO)
        self.button_height = int(min_dimension * BUTTON_HEIGHT_RATIO)
        self.button_margin = int(min_dimension * BUTTON_MARGIN_RATIO)
        self.font_size = int(min_dimension * FONT_SIZE_RATIO)        

    def create_players(self, num_players: int):
        """Создание игроков (1 человек + боты)"""
        self.players.append(Player("You", is_human=True))
        
        for i in range(1, num_players):
            self.players.append(Player(f"Bot {i}"))
        
        # Назначаем дилера
        self.players[1].is_dealer = True
        
    def create_buttons(self) -> List[Button]:
        """Создание интерфейсных кнопок"""
        buttons = []
        button_y = self.screen_height - self.button_height - self.button_margin
        
        # Fold button
        fold_btn = Button(
            self.screen_width // 2 - self.button_width * 1.5 - self.button_margin,
            button_y,
            self.button_width,
            self.button_height,
            "Fold"
        )
        buttons.append(fold_btn)
        
        # Call button
        call_btn = Button(
            self.screen_width // 2 - self.button_width // 2,
            button_y,
            self.button_width,
            self.button_height,
            "Call"
        )
        buttons.append(call_btn)
        
        # Raise button
        raise_btn = Button(
            self.screen_width // 2 + self.button_width * 0.5 + self.button_margin,
            button_y,
            self.button_width,
            self.button_height,
            "Raise"
        )
        buttons.append(raise_btn)
        
        return buttons
    
    def update_buttons_position(self):
        """Обновление позиции кнопок при изменении размера окна"""
        button_y = self.screen_height - self.button_height - self.button_margin
        
        # Fold button
        self.buttons[0].update_position(
            self.screen_width // 2 - self.button_width * 1.5 - self.button_margin,
            button_y,
            self.button_width,
            self.button_height
        )
        
        # Call button
        self.buttons[1].update_position(
            self.screen_width // 2 - self.button_width // 2,
            button_y,
            self.button_width,
            self.button_height
        )
        
        # Raise button
        self.buttons[2].update_position(
            self.screen_width // 2 + self.button_width * 0.5 + self.button_margin,
            button_y,
            self.button_width,
            self.button_height
        )
    
    def deal_test_cards(self):
        """Раздача тестовых карт игрокам"""
        # Тестовый набор карт
        test_cards = [
            [Card("♥", "A"), Card("♦", "K")],
            [Card("♣", "10"), Card("♠", "2")],
            [Card("♦", "Q"), Card("♥", "7")],
            [Card("♠", "9"), Card("♣", "J")],
            [Card("♥", "8"), Card("♦", "4")],
            [Card("♣", "3"), Card("♠", "Q")],
            [Card("♦", "6"), Card("♥", "10")],
            [Card("♠", "5"), Card("♣", "K")]
        ]
        
        # Раздача карт игрокам
        for i, player in enumerate(self.players):
            if i < len(test_cards):
                for card in test_cards[i]:
                    player.deal_card(card)
    
    def arrange_players(self):
        """Расположение игроков вокруг стола"""
        center_x = self.screen_width // 2
        center_y = (self.screen_height // 2) - self.screen_height*0.05
        
        # Рассчитываем расстояние от края стола до игроков
        player_offset = self.table_radius * 1.1# 1.5 радиуса стола
        
        # Распределение игроков по кругу
        angle_step = 2 * math.pi / len(self.players)
        start_angle = 90 # Начинаем снизу (270 градусов)
        
        for i, player in enumerate(self.players):
            angle_rad = math.radians(start_angle + i * (360 / len(self.players)))
            
            # Позиция относительно центра стола
            x = center_x + player_offset * math.cos(angle_rad)
            y = center_y + player_offset * math.sin(angle_rad)
            
            player.position = (int(x), int(y)-(self.card_height//2))
    
    def draw_table(self):
        """Отрисовка покерного стола"""
        # Фон
        self.screen.fill(BACKGROUND_COLOR)
        
        # Центр стола
        center = (self.screen_width // 2, (self.screen_height // 2)-self.screen_height*0.05)
        
        # Стол
        pygame.draw.circle(self.screen, TABLE_COLOR, center, self.table_radius)
        
        # Внутренний круг стола (для красивого вида)
        inner_radius = self.table_radius * 0.7
        pygame.draw.circle(self.screen, (20, 90, 50), center, inner_radius)
        
        # Логотип в центре стола
        title = self.title_font.render("POKER", True, PLAYER_TEXT_COLOR)
        title_rect = title.get_rect(center=center)
        self.screen.blit(title, title_rect)
        
        # Общие карты
        if self.community_cards:
            card_spacing = self.card_width
            total_width = len(self.community_cards) * card_spacing
            start_x = center[0] - total_width // 2
            y = center[1] - self.card_height // 2
            
            for i, card in enumerate(self.community_cards):
                card_x = start_x + i * card_spacing
                card.render(self.screen, card_x, y, self.card_width, self.card_height, True) 
    def draw_game_info(self):
        """Отрисовка информации о игре"""
        # Банк
        pot_text = self.font.render(f"Pot: ${self.pot}", True, PLAYER_TEXT_COLOR)
        self.screen.blit(pot_text, (20, 20))
        
        # Текущая ставка
        bet_text = self.font.render(f"Current Bet: ${self.current_bet}", True, PLAYER_TEXT_COLOR)
        self.screen.blit(bet_text, (20, 50))
        
        # Стадия игры
        stage_text = self.font.render("Stage: Turn", True, PLAYER_TEXT_COLOR)
        self.screen.blit(stage_text, (20, 80))
        
        # Активный игрок
        active_text = self.font.render("Active: You", True, PLAYER_TEXT_COLOR)
        self.screen.blit(active_text, (20, 110))
    
    def handle_events(self):
        """Обработка событий игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Обработка изменения размера окна
            elif event.type == pygame.VIDEORESIZE:
                # Устанавливаем минимальные размеры окна
                width = max(MIN_WIDTH, event.w)
                height = max(MIN_HEIGHT, event.h)
                
                # Создаем новую поверхность
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                self.screen_width = width
                self.screen_height = height
                
                # Пересчитываем размеры элементов
                self.calculate_sizes()
                
                # Обновляем шрифты
                self.font = pygame.font.SysFont('Arial', self.font_size)
                self.title_font = pygame.font.SysFont('Arial', int(self.font_size * 1.5), bold=True)
                
                # Обновляем позиции игроков и кнопок
                self.arrange_players()
                self.update_buttons_position()
            
            # Обработка нажатий кнопок
            for button in self.buttons:
                if button.handle_event(event):
                    print(f"Button pressed: {button.text}")
    
    def render(self):
        """Отрисовка всего игрового состояния"""
        # Рисуем стол и общие карты
        self.draw_table()
        
        # Рисуем игроков и их карты
        for player in self.players:
            player.render(self.screen, self.card_width, self.card_height, self.font)
        
        # Рисуем кнопки
        for button in self.buttons:
            button.draw(self.screen, self.font)
        
        # Рисуем информацию о игре
        self.draw_game_info()
    
    def run(self):
        """Основной игровой цикл"""
        while True:
            self.handle_events()
            self.render()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    num_players = 6
    
    game = PokerGame(num_players)
    game.run()
