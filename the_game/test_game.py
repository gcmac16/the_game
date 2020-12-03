import unittest

from .card import Card
from .deck import Deck
from .game import Game
from .player import Player


def test_deal_1_player():
    deck = Deck()
    p1 = Player(1)
    p1.draw_cards(deck)

    assert len(p1.hand) == 1
    assert p1.hand == [Card(2)]
    assert len(deck.cards) == 97
    assert set(p1.hand).isdisjoint(deck.cards)

def test_multi_deal():
    deck = Deck()
    p1 = Player(1)
    p1.draw_cards(deck, 5)

    assert len(p1.hand) == 5
    assert p1.hand == [Card(i) for i in range(2, 7)]
    assert p1.hand == [2, 3, 4, 5, 6]
    assert len(deck.cards) == 93
    assert set(p1.hand).isdisjoint(deck.cards)

def test_game_deal():
    game = Game(4, 6)
    game.setup_game()
    game.deal_cards()

    assert len(game.players) == 4
    for player in game.players.values():
        assert len(player.hand) == 6

    assert len(game.deck.cards) == 74

def test_shuffle():
    game = Game(4, 6)
    game.setup_game()
    game.deal_cards()

    # this is a really simple way to test that the game shuffles 
    # the deck. we check that after shuffling the first five values
    # aren't what they would be if it was still sorted. This will fail
    # once every 8B times when the random number generator does indeed
    # output that starting sequence. Personally, I like those odds
    assert game.deck.cards[:5] != [2, 3, 4, 5, 6]

