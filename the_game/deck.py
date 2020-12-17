import random
from typing import (
    Optional,
)

from .card import Card


class Deck(object):

    def __init__(self, seed: Optional[int] = None, card_range: range = range(2, 100)):
        self.cards = [Card(i) for i in card_range]
        self.seed = seed

    def shuffle(self):
        random.Random(self.seed).shuffle(self.cards)

    def draw(self):
        return self.cards.pop(0)

    def __len__(self):
        return len(self.cards)
