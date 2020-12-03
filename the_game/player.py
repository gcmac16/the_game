from typing import (
    List,
)
from .card import Card


class Player(object):

    def __init__(self, player_id: int):
        self.player_id = player_id
        self.hand = []

    def draw_cards(self, deck: List[Card], n: int = 1):
        for _ in range(n):
            self.hand.append(deck.draw())  # note this mutates deck "in place"

    def __repr__(self):
        return f"Player {self.player_id}: [{', '.join([str(card.value) for card in self.hand])}]"
