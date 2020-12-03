from random import (
    shuffle,
)

from .player import Player
from .deck import Deck
from .card import Card


class Game(object):

    def __init__(self, n_players: int, n_cards_in_hand: int):
        self.players = {pid: Player(pid) for pid in range(n_players)}
        self.n_cards_start = n_cards_in_hand

        self.piles = {
            'p1_up': [Card(1)],
            'p2_up': [Card(1)],
            'p1_down': [Card(100)],
            'p2_down': [Card(100)]
        }

    def deal_cards(self):
        for _ in range(self.n_cards_start):
            for player in self.players.values():
                player.draw_cards(self.deck)

    def setup_game(self):
        self.deck = Deck()
        self.deck.shuffle()
