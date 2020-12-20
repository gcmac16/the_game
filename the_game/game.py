import json
from random import (
    shuffle,
)
from typing import (
    Optional,
)

from .card import Card
from .deck import Deck
from .exceptions import NoValidMoveError
from .move import Move
from .player import Player


class Game(object):

    def __init__(
            self, 
            n_players: int, 
            n_cards_in_hand: int,
            logger = None,
            deck_seed: Optional[int] = None,
            player_style: str = 'optimized',
            first_move_selection: str = 'first_player',
    ):
        self.players = {pid: Player(pid, player_style) for pid in range(n_players)}
        self.n_cards_start = n_cards_in_hand
        self.active_player_id = None
        self.player_style = player_style
        self.deck = Deck(deck_seed)
        self.logger = logger
        self.first_move_selection = first_move_selection

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
    
    @property
    def n_cards_to_play(self):
        if len(self.deck) > 0:
            return 2
        return 1

    @property
    def game_won(self):
        """Two criteria for winning game: deck is empty and all players have empty hand"""
        if len(self.deck) == 0 and sum([len(player.hand) for player in self.players.values()]) == 0:
            return True
        return False

    def find_lowest_first_move_increment(self):
        min_increment = 100
        best_move_player_id = None

        for player_id, player in self.players.items():
            best_move = player.get_cards_for_move(self.piles)
            total_increment = sum([move.increment for move in best_move])
            if total_increment < min_increment:
                min_increment = total_increment
                best_move_player_id = player_id

        return best_move_player_id

    def set_active_player_id(self):
        if self.active_player_id is None:
            if self.first_move_selection == 'first_player':
                self.active_player_id = 0
            elif self.first_move_selection == 'optimized':
                self.active_player_id = self.find_lowest_first_move_increment()
            else:
                raise ValueError("First move selection must be 'first_player' or 'optimized'")
            return  

        if (pid := self.active_player_id + 1) < len(self.players):
            self.active_player_id = pid
        else:
            self.active_player_id = 0

    def log_move(self, move: Move):
        if self.logger is None:
            return
        log_body = {
            'active_player_id': self.active_player_id,
            'deck': self.deck.cards,
            'piles': self.piles,
            'players': {pid: player.hand for pid, player in self.players.items()},
            'move_str': f"Player {self.active_player_id} played {move.card} on {move.pile_id}"
        }

        self.logger.info(json.dumps(log_body))

    def make_move(self, print_move: bool = True):
        active_player = self.players[self.active_player_id]
        moves = active_player.get_cards_for_move(self.piles, n_cards_to_play=self.n_cards_to_play)

        if len(moves) == 0:
            raise NoValidMoveError
        
        for move in moves:
            self.piles[move.pile_id].append(move.card)
            active_player.hand.remove(move.card)
            self.log_move(move)
         
        try:
            active_player.draw_cards(self.deck, n=len(moves))
        except IndexError:
            pass  # if the deck is empty, don't draw any cards

        self.set_active_player_id()
