from enum import Enum
import random
from typing import List, Dict
import time

class Card:
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()

    def reset(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Card]:
        return [self.cards.pop() for _ in range(num_cards)]

class Player:
    def __init__(self, is_bot: bool, stack: int = 1000):
        self.is_bot: bool = is_bot
        self.stack: int = stack
        self.cards: List[Card] = []
        self.current_bet: int = 0
        self.is_active: bool = True
        self.is_all_in: bool = False

class GameStage(Enum):
    PREFLOP = "pre-flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class PokerGame:
    def __init__(self, num_players: int = 6):
        self.players: List[Player] = self._initialize_players(num_players)
        self.deck: Deck = Deck()
        self.community_cards: List[Card] = []
        self.pot: int = 0
        self.current_bet: int = 0
        self.dealer_position: int = 0
        self.stage: GameStage = GameStage.PREFLOP
        self.game_over: bool = False
        self.waiting_for_human_input: bool = False
        self.current_player_index: int = 0
        self.human_player_index: int = num_players - 1
        self.last_raiser: int = -1
        self.active_players: List[Player] = []
        self.betting_round_complete: bool = False
        self.last_action_time: float = 0
        self.action_delay: float = 1.5  # Задержка между действиями ботов

    def _initialize_players(self, num_players: int) -> List[Player]:
        return [Player(is_bot=True) for _ in range(num_players-1)] + [Player(is_bot=False)]

    def start_new_hand(self):
        self.community_cards.clear()
        self.deck.reset()
        
        for player in self.players:
            player.cards = self.deck.deal(2)
            player.is_active = True
            player.current_bet = 0
            player.is_all_in = False
        
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self._post_blinds()
        self.active_players = [p for p in self.players if p.is_active]
        self.stage = GameStage.PREFLOP
        self.current_player_index = (self.dealer_position + 3) % len(self.players)
        self.last_raiser = -1
        self.betting_round_complete = False
        self.current_bet = 20  # Большой блайнд

    def _post_blinds(self):
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (sb_pos + 1) % len(self.players)
        small_blind = 10
        big_blind = 20
        
        self.players[sb_pos].stack -= small_blind
        self.players[sb_pos].current_bet = small_blind
        self.players[bb_pos].stack -= big_blind
        self.players[bb_pos].current_bet = big_blind
        self.pot += small_blind + big_blind
        self.current_bet = big_blind

    def game_step(self):
        current_time = time.time()
        
        # Пауза между действиями
        if current_time - self.last_action_time < self.action_delay:
            return
            
        self.last_action_time = current_time
        
        if self.stage == GameStage.SHOWDOWN:
            self._handle_showdown()
            self.start_new_hand()
            self.action_delay = 5.0  # Долгая пауза перед новой раздачей
            return

        if self.betting_round_complete:
            self._advance_stage()
            self.action_delay = 3.0  # Пауза перед новой стадией
            return
        else:
            self._handle_player_turn()
            self.action_delay = 1.0  # Обычная пауза между ходами

    def _handle_player_turn(self):
        if self.current_player_index >= len(self.active_players):
            self.current_player_index = 0
            
        player = self.active_players[self.current_player_index]
        
        # Пропускаем неактивных игроков
        if not player.is_active or player.is_all_in:
            self._next_player()
            return
            
        if player.is_bot:
            decision = self._bot_decision(player)
            self._process_decision(player, decision)
            self._next_player()
        else:
            self.waiting_for_human_input = True

    def make_human_decision(self, decision: str):
        player = self.active_players[self.current_player_index]
        self._process_decision(player, decision)
        self.waiting_for_human_input = False
        self._next_player()

    def _next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.active_players)
        
        # Проверяем, завершился ли раунд ставок
        if self.current_player_index == 0 or self._betting_round_complete():
            self.betting_round_complete = True

    def _betting_round_complete(self):
        # Все активные игроки сделали ставки равными текущей ставке или сбросились
        active_players = [p for p in self.active_players if p.is_active and not p.is_all_in]
        
        if not active_players:
            return True
            
        # Проверяем, все ли сделали равные ставки
        all_bets_equal = all(p.current_bet == self.current_bet for p in active_players)
        
        # Проверяем, все ли игроки сделали ход
        all_players_acted = all(p.current_bet > 0 or not p.is_active for p in self.active_players)
        
        return all_bets_equal and all_players_acted

    def _bot_decision(self, player: Player) -> str:
        hand_strength = random.uniform(0, 1)
        
        if not player.is_active:
            return 'fold'
        
        # Вероятностная модель принятия решений
        if self.current_bet == 0:  # Нет ставок, можно чекать
            if hand_strength > 0.7:
                return 'raise'
            elif hand_strength > 0.3:
                return 'call'
            else:
                return 'fold'
        else:  # Уже есть ставки
            if hand_strength > 0.8:
                return 'raise'
            elif hand_strength > 0.5:
                return 'call'
            else:
                return 'fold'

    def _process_decision(self, player: Player, decision: str):
        if decision == 'fold':
            player.is_active = False
        elif decision == 'call':
            call_amount = self.current_bet - player.current_bet
            if call_amount > player.stack:
                call_amount = player.stack
                player.is_all_in = True
                
            player.stack -= call_amount
            player.current_bet += call_amount
            self.pot += call_amount
        elif decision == 'raise':
            raise_amount = self.current_bet * 2
            if raise_amount > player.stack:
                raise_amount = player.stack
                player.is_all_in = True
                
            player.stack -= raise_amount
            player.current_bet += raise_amount
            self.pot += raise_amount
            self.current_bet = raise_amount
            self.last_raiser = self.current_player_index

    def _advance_stage(self):
        stages = [GameStage.PREFLOP, GameStage.FLOP, 
                 GameStage.TURN, GameStage.RIVER]
        idx = stages.index(self.stage)
        
        if idx < len(stages) - 1:
            self.stage = stages[idx + 1]
            self.betting_round_complete = False
            self.current_player_index = (self.dealer_position + 1) % len(self.active_players)
            self.last_raiser = -1
            self.current_bet = 0
            
            # Сбрасываем текущие ставки игроков для нового раунда
            for player in self.players:
                player.current_bet = 0
            
            # Раздаем общие карты
            cards_to_deal = 3 if self.stage == GameStage.FLOP else 1
            self.community_cards.extend(self.deck.deal(cards_to_deal))
            
            # Обновляем список активных игроков
            self.active_players = [p for p in self.players if p.is_active]
        else:
            self.stage = GameStage.SHOWDOWN

    def _handle_showdown(self):
        active_players = [p for p in self.players if p.is_active]
        if len(active_players) > 0:
            # Просто выбираем случайного победителя для упрощения
            winner = random.choice(active_players)
            winner.stack += self.pot
        
        self.pot = 0

    def get_game_state(self) -> Dict:
        return {
            'community_cards': self.community_cards,
            'pot': self.pot,
            'players': [
                {
                    'cards': p.cards,
                    'stack': p.stack,
                    'current_bet': p.current_bet,
                    'is_active': p.is_active,
                    'is_bot': p.is_bot
                } for p in self.players
            ],
            'current_bet': self.current_bet,
            'waiting_for_input': self.waiting_for_human_input,
            'stage': self.stage.value
        }
