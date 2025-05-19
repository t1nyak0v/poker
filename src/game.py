import random
from enum import Enum
from typing import List, Dict

import player

MIN_BET = 10
SMALL_BLIND = 10
BIG_BLIND = 20

class GameStage(Enum):
    PREFLOP = "pre-flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class Game():
    def __init__(self, players: List[player.Player] = []):
        self.players: List[player.Player] = players
        self.active_players: List[player.Player] = []

        self.dealer_position: int = 0

        self.pot: int = 0
        self.deck: Game.Deck = Game.Deck()
        self.current_bet: int = 0
        self.community_cards: List[Game.Card] = []

        self.game_stage: GameStage = GameStage.PREFLOP
        self.betting_round_complite: bool = False
        self.is_game_going: bool = True

    class Card:
        def __init__(self, rank:str, suit: str):
            self.rank = rank
            self.suit = suit

    class Deck:
        def __init__(self) -> None:
            self.cards: List[Game.Card] = []
            self.reset()

        def reset(self) -> None:
            self.cards = self._generate()

        def _generate(self) -> List:
            suits = ['♥', '♦', '♣', '♠']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            deck = [Game.Card(rank, suit) for suit in suits for rank in ranks]
            return deck

        def shuffle(self) -> None:
            random.shuffle(self.cards)

        def deal(self, num_cards: int) -> List: # it should be List[Game.Card] here, but for some reason it doesn't work. Someday i'll have to figure out
            return [self.cards.pop() for _ in range(num_cards)]

    def _initialize_players(self, num_players: int) -> List[player.Player]:
        players: List[player.Player] = []
        players.append(player.UserPlayer())

        for _ in range(num_players - 1):
            players.append(player.BotPlayer())

        return players


    def start_new_hangout(self):
        self.community_cards.clear()
        self.deck.reset()
        self.deck.shuffle()

        for player in self.players:
            player.set_hand(self.deck.deal(2))

        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self._post_blinds()

        self.active_players = [player for player in self.players if player.is_active]
        self.stage = GameStage.PREFLOP
        self.betting_round_complite = False

    def _post_blinds(self):
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (sb_pos + 1) % len(self.players)

        self.players[sb_pos].stack -= SMALL_BLIND
        self.players[bb_pos].stack -= BIG_BLIND
        self.pot += SMALL_BLIND + BIG_BLIND
        self.current_bet = BIG_BLIND

    def game_loop(self) -> None:
        while self.is_game_going:
            self.start_new_hangout()

            while self.stage != GameStage.SHOWDOWN:
                self._handle_betting_round()
                self._advance_stage()

            self._handle_showdown()

            if self._check_game_over():
                self.is_game_going = False

    def _handle_betting_round(self):
        self.betting_round_complite = False
        last_raiser = None
        current_player_index = (self.dealer_position + 3) % len(self.players)

        while not self.betting_round_complite:
            current_player = self.active_players[current_player_index]

            if current_player.is_active and not current_player.is_all_in:
                decision = current_player.get_decision()
                self._process_decision(current_player, decision)

                if decision == "raise":
                    last_raiser = current_player_index

            current_player_index = (current_player_index + 1) % len(self.active_players)

            if current_player_index == last_raiser:
                self.betting_round_complite = True

    def _advance_stage(self):
        stage_order = [
                GameStage.PREFLOP,
                GameStage.FLOP,
                GameStage.TURN,
                GameStage.RIVER,
                GameStage.SHOWDOWN
            ]

        current_index = stage_order.index(self.stage)

        if current_index < len(stage_order) - 1:
            self.stage = stage_order[current_index + 1]

            if self.stage == GameStage.FLOP:
                self.community_cards.extend(self.deck.deal(3))
            elif self.stage in [GameStage.TURN, GameStage.RIVER]:
                self.community_cards.extend(self.deck.deal(1))

    def _handle_showdown(self, player: player.Player) -> str:
        return ""
    
    def _check_game_over(self):
        pass

    def _process_decision(self, current_player, decision):
        pass
