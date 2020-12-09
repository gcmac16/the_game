import unittest

from .card import Card
from .deck import Deck
from .game import Game
from .player import Move
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


def test_valid_moves_first_pass_one_card():
    player = Player(1)
    player.hand = [Card(50)]

    g = Game(4, 6)
    valid_moves = player.find_valid_moves_first_pass(g.piles)
    assert len(valid_moves) == 4
    assert [vm.increment for vm in valid_moves] == [49, 49, 50, 50]
    
def test_valid_moves_first_pass_diff_ten():
    player = Player(1)
    player.hand = [Card(50)]

    piles = {
        'p1_up': [Card(40)],
        'p2_up': [Card(60)], 
        'p1_down': [Card(100)],
        'p2_down': [Card(10)]
    }
    valid_moves = player.find_valid_moves_first_pass(piles)

    assert len(valid_moves) == 3
    assert valid_moves[0].increment == 10
    assert valid_moves[1].increment == -10
    assert valid_moves[2].increment == 50
    assert 'p2_down' not in [vm.pile for vm in valid_moves]
    
def test_valid_sequences_simple():
    player = Player(1)
    player.hand = [Card(3), Card(4)]

    piles = {
        'p1_up': [Card(1)]
    }
    valid_sequences = player.find_valid_moves(piles)

    assert len(valid_sequences) == 1
    assert valid_sequences[0][0] == Move(Card(3), 'p1_up', 2)
    assert valid_sequences[0][1] == Move(Card(4), 'p1_up', 1)


def test_valid_sequences_two_piles():
    player = Player(1)
    player.hand = [Card(50), Card(55)]

    piles = {
        'p1_up': [Card(1)],
        'p1_down': [Card(100)],
    }
    valid_sequences = player.find_valid_moves(piles)

    assert len(valid_sequences) == 4
    assert valid_sequences[0] == [Move(Card(50), 'p1_up', 49), Move(Card(55), 'p1_down', 45)]
    assert valid_sequences[1] == [Move(Card(50), 'p1_down', 50), Move(Card(55), 'p1_up', 54)]
    assert valid_sequences[2] == [Move(Card(50), 'p1_up', 49), Move(Card(55), 'p1_up', 5)]
    assert valid_sequences[3] == [Move(Card(55), 'p1_down', 45), Move(Card(50), 'p1_down', 5)]

def test_evaluate_moves():
    moves = [
        [Move(Card(50), 'p1_up', 49), Move(Card(55), 'p1_down', 45)],
        [Move(Card(50), 'p1_down', 50), Move(Card(55), 'p1_up', 54)],
        [Move(Card(50), 'p1_up', 49), Move(Card(55), 'p1_up', 5)],
        [Move(Card(55), 'p1_down', 45), Move(Card(50), 'p1_down', 5)]
    ]

    player = Player(1)
    selected_move = player.evaluate_moves(moves)

    assert isinstance(selected_move, list)
    assert selected_move == moves[3]


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
    

def test_make_move_one_card():
    player = Player(1)
    piles = {'p1_up': [Card(50)], 'p1_down': [Card(75)]}

    player.hand = [Card(35), Card(51), Card(73)]
    move = player.make_move(piles, min_cards=1)
    assert len(move) == 1
    assert move[0] == Move(Card(51), 'p1_up', 1)


def test_make_move_full():
    game = Game(2, 5)
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
    

