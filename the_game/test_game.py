import unittest
import pytest

from .card import Card
from .deck import Deck
from .exceptions import NoValidMoveError
from .game import Game
from .move import Move
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
    assert game.deck.cards[:5] != [Card(i) for i in range(2, 7)]


def test_valid_moves_one_card():
    player = Player(1)
    player.hand = [Card(50)]

    g = Game(4, 6)
    valid_moves = player.find_valid_moves(g.piles)
    assert len(valid_moves) == 4
    assert [vm.increment for vm in valid_moves] == [49, 49, 50, 50]

    
def test_valid_moves_diff_ten():
    player = Player(1)
    player.hand = [Card(50)]

    piles = {
        'p1_up': [Card(40)],
        'p2_up': [Card(60)], 
        'p1_down': [Card(100)],
        'p2_down': [Card(10)]
    }
    valid_moves = player.find_valid_moves(piles)

    assert len(valid_moves) == 3
    assert valid_moves[0].increment == 10
    assert valid_moves[1].increment == -10
    assert valid_moves[2].increment == 50
    assert 'p2_down' not in [vm.pile_id for vm in valid_moves]
    

def test_valid_sequences_simple_greedy():
    player = Player(1)
    player.hand = [Card(3), Card(4)]

    piles = {
        'p1_up': [Card(1)]
    }
    moves = player.get_cards_for_move(piles)
    
    assert len(moves) == 2
    assert moves[0] == Move(Card(3), 'p1_up', Card(1))
    assert moves[1] == Move(Card(4), 'p1_up', Card(3))
    

def test_valid_sequences_two_piles():
    player = Player(1)
    player.hand = [Card(50), Card(55)]

    piles = {
        'p1_up': [Card(1)],
        'p1_down': [Card(100)],
    }
    moves = player.get_cards_for_move(piles)

    assert len(moves) == 2
    assert moves[0] == Move(Card(55), 'p1_down', Card(100))
    assert moves[1] == Move(Card(50), 'p1_down', Card(55))
    
    
def test_valid_sequences_simple_optimized():
    player = Player(1, player_style='optimized')
    
    player.hand = [Card(95), Card(90), Card(85)]
    piles = {
        'p1_down': [Card(91)],
    }
    
    moves = player.get_cards_for_move(piles)
    
    assert len(moves) == 2
    assert moves[0] == Move(Card(85), 'p1_down', Card(91))
    assert moves[1] == Move(Card(95), 'p1_down', Card(85))
    
    
def test_set_active_player():
    g = Game(4, 6)
    g.setup_game()

    assert g.active_player_id == 0
    g.set_active_player_id()
    assert g.active_player_id == 1
    g.set_active_player_id()
    assert g.active_player_id == 2
    g.set_active_player_id()
    assert g.active_player_id == 3
    g.set_active_player_id()
    assert g.active_player_id == 0
    

def test_no_duplicate_cards_in_move():

    player = Player(1, player_style='optimized')
    player.hand = [Card(10), Card(75), Card(94), Card(35), Card(21)]
    
    piles = {
        'p1_up': [Card(1)],
        'p2_up': [Card(1)],
        'p1_down': [Card(100)],
        'p2_down': [Card(100)],
    }
    
    moves = player.get_cards_for_move(piles)
    
    assert len(moves) == 2
    assert set(moves) == {Move(Card(94), 'p1_down', Card(100)), Move(Card(10), 'p1_up', Card(1))}
    
    
def test_make_move_full():
    game = Game(2, 5, player_style='optimized')
    game.players[0].hand = [Card(10), Card(75), Card(94), Card(35), Card(21)]
    game.players[1].hand = [Card(2), Card(88), Card(87), Card(55), Card(23)]
    game.active_player_id = 0

    game.make_move()

    assert len(game.piles['p1_up']) == 2
    assert game.piles['p1_up'][-1] == Card(10)
    assert game.piles['p1_down'][-1] == Card(94)
    assert sum([len(pile) for pile in game.piles.values()]) == 6 
    assert len(game.players[0].hand) == 5
    assert game.players[0].hand[-2:] == [Card(2), Card(3)]
    assert game.active_player_id == 1

    game.make_move()

    assert len(game.piles['p2_up']) == 2
    assert len(game.piles['p1_down']) == 3
    assert game.piles['p1_down'][-1] == Card(88)
    assert len(game.players[1].hand) == 5
    assert sum([len(pile) for pile in game.piles.values()]) == 8
    assert game.players[1].hand[-2:] == [Card(4), Card(5)]
    assert game.active_player_id == 0
    
def test_end_of_game_one_card_need_two():
    player = Player(1)
    player.hand = [Card(8), Card(26), Card(73)]
    
    piles = {
        'p1_up': [Card(80)],
        'p2_up': [Card(85)],
        'p1_down': [Card(10)],
        'p2_down': [Card(15)]
    }
    
def test_no_valid_move_error():
    g = Game(2, 2)
    g.active_player_id = 0
    g.piles = {
        'p1_up': [Card(70)],
        'p1_down': [Card(20)],
    }

    g.players[0].hand = [Card(50), Card(55), Card(43)]
    
    with pytest.raises(NoValidMoveError):
        g.make_move()

def test_no_valid_move_play_one_card():
    g = Game(2, 2)
    g.active_player_id = 0
    g.piles = {
        'p1_up': [Card(70)],
        'p2_down': [Card(5)],
    }

    g.players[0].hand = [Card(50), Card(55)]
    g.deck = []

    assert g.n_cards_to_play == 1

    with pytest.raises(NoValidMoveError):
        g.make_move()


def test_game_over():
    g = Game(2, 2)
    g.players[0].hand = [Card(10)]
    g.players[1].hand = []
    g.deck = Deck(card_range=range(0))
    g.active_player_id = 0

    g.piles = {'p1_down': [Card(11)]}
    assert g.n_cards_to_play == 1
    g.make_move()

    assert g.game_won

  
def test_find_lowest_first_move_increment():
    g = Game(3, 6, player_style='optimized', first_move_selection='optimized')
    g.players[0].hand = [Card(10), Card(15), Card(58), Card(85)]
    g.players[1].hand = [Card(94), Card(88), Card(5), Card(45)]
    g.players[2].hand = [Card(3), Card(23), Card(48), Card(52)]

    assert g.find_lowest_first_move_increment() == 1

