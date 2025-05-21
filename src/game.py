from enum import Enum
import random
from typing import List, Dict

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
        self.active_players: List[Player] = []
        self.game_over: bool = False
        self.waiting_for_human_input: bool = False
        self.current_player_index: int = 0
        self.human_player_index: int = num_players - 1
        self.last_raiser: int = -1

    def _initialize_players(self, num_players: int) -> List[Player]:
        return [Player(is_bot=True) for _ in range(num_players-1)] + [Player(is_bot=False)]

    def start_new_hand(self):
        self.community_cards.clear()
        self.deck.reset()
        
        for player in self.players:
            player.cards = self.deck.deal(2)
            player.is_active = True
            player.current_bet = 0
        
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self._post_blinds()
        self.active_players = [p for p in self.players if p.is_active]
        self.stage = GameStage.PREFLOP
        self.current_player_index = (self.dealer_position + 3) % len(self.players)
        self.last_raiser = -1

    def _post_blinds(self):
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (sb_pos + 1) % len(self.players)
        small_blind = 10
        big_blind = 20
        
        self.players[sb_pos].stack -= small_blind
        self.players[bb_pos].stack -= big_blind
        self.pot += small_blind + big_blind
        self.current_bet = big_blind

    def game_step(self):
        if self.stage == GameStage.SHOWDOWN:
            self._handle_showdown()
            self.start_new_hand()
            return

        if self._betting_round_complete():
            self._advance_stage()
        else:
            self._handle_player_turn()

    def _handle_player_turn(self):
        player = self.active_players[self.current_player_index]
        
        if player.is_active:
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
        if self.current_player_index == self.last_raiser:
            self.last_raiser = -1
            self.current_bet = 0
            return

    def _betting_round_complete(self):
        return self.last_raiser == -1 and all(
            p.current_bet == self.current_bet or not p.is_active 
            for p in self.active_players
        )

    def _bot_decision(self, player: Player) -> str:
        hand_strength = random.uniform(0, 1)
        if hand_strength > 0.8:
            return 'raise'
        elif hand_strength > 0.4 or self.current_bet == 0:
            return 'call'
        else:
            return 'fold'

    def _process_decision(self, player: Player, decision: str):
        if decision == 'fold':
            player.is_active = False
        elif decision == 'call':
            call_amount = self.current_bet - player.current_bet
            player.stack -= call_amount
            player.current_bet += call_amount
            self.pot += call_amount
        elif decision == 'raise':
            raise_amount = self.current_bet * 2
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
            cards_to_deal = 3 if self.stage == GameStage.FLOP else 1
            self.community_cards.extend(self.deck.deal(cards_to_deal))
        else:
            self.stage = GameStage.SHOWDOWN

    def _handle_showdown(self):
        active_players = [p for p in self.players if p.is_active]
        if len(active_players) > 1:
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
            'waiting_for_input': self.waiting_for_human_input
        }
