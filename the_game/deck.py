from random import (
    shuffle,
)

from .card import Card


class Deck(object):

    def __init__(self):
        self.cards = [Card(i) for i in range(2, 100)]

    def shuffle(self):
        shuffle(self.cards)

    def draw(self):
        return self.cards.pop(0)

    def __len__(self):
        return len(self.cards)
