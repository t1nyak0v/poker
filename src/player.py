

import random


class Player():
    def __init__(self, hand=None):
        self.hand = hand if hand is not None else []
        self.position: int = -1

        self.current_bet: int = 0
        self.stack: int = 1000

        self.is_hand_known: bool = False
        self.is_active: bool = True
        self.is_all_in: bool = False

    def set_hand(self, hand) -> None:
        self.hand = hand

    def clear_hand(self) -> None:
        self.hand.clear()

    def open_hand(self) -> None:
        self.is_hand_known = True

    def set_position(self, position):
        self.position = position

    def get_hand(self) -> list:
        return self.hand

    def get_decision(self) -> str:
        return random.choice(["fold", "raise", "call"])

    # DEBUG

    def __str__(self) -> str:
        hand = "Cards: " + ", ".join(self.hand) if self.hand else "No cards"
        position = "Position: " + ", ".join(str(self.position)) if self.position != -1 else "No position"

        out = hand + "\n" + position
        return out


class UserPlayer(Player):
    def __init__(self, hand=None):
        super().__init__(hand)


class BotPlayer(Player):
    def __init__(self, hand=None):
        super().__init__(hand)

    def get_hand(self) -> list:
        return super().get_hand() if self.is_hand_known else ["?? ??",""]
