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
        self.active_player_id = None
        self.deck = Deck()

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
        self.deck.shuffle()
        self.set_active_player_id()

    def set_active_player_id(self):
        if self.active_player_id is None:
            # TODO: on first setup, we should check for player that 
            # has the best first move possible and then go from there
            self.active_player_id = 0
            return

        if (pid := self.active_player_id + 1) < len(self.players):
            self.active_player_id = pid
        else:
            self.active_player_id = 0

    def make_move(self):
        active_player = self.players[self.active_player_id]
        if len(self.deck) > 0:
            moves = active_player.make_move(self.piles, min_cards=2)
        else:
            moves = active_player.make_move(self.piles, min_cards=1)

        for move in moves:
            self.piles[move.pile].append(move.card)
            active_player.hand.remove(move.card)
         
        try:
            active_player.draw_cards(self.deck, n=len(moves))
        except IndexError:
            pass  # if the deck is empty, don't draw any cards

        self.set_active_player_id()
