from typing import List

import game
import player

from window import Window

PLAYERS_NUM = 6 # players number + dealer

def main():
    players: List[player.Player] = []

    user = player.UserPlayer()
    players.append(user)

    for i in range(PLAYERS_NUM - 1):
        players.append(player.BotPlayer())

    master = game.Game(players)
    # window = Window()
    # window.update_players_cards([player.get_hand() for player in players])
    # window.run()
    master.game_loop()

if __name__ == "__main__":
    main()
