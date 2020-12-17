import copy
from dataclasses import dataclass
from typing import (
    Dict,
    List,
)

from .card import Card
from .move import Move


class Player(object):

    def __init__(self, player_id: int, player_style: str = 'greedy'):
        self.player_id = player_id
        self.hand = []
        self.player_style = player_style

    def draw_cards(self, deck: List[Card], n: int = 1):
        for _ in range(n):
            self.hand.append(deck.draw())  # note this mutates deck "in place"

    def __repr__(self):
        return f"Player {self.player_id}: [{', '.join([str(card.value) for card in self.hand])}]"

    def get_cards_for_move(
        self,
        card_piles: Dict[str, List[Card]], 
        n_cards_to_play: int = 2
    ) -> List[Move]:
        # TODO: Break up the logic into their own functions
        moves = []
        card_piles_ = copy.deepcopy(card_piles)
        if self.player_style == 'greedy':
            for _ in range(n_cards_to_play):
                best_move = self.find_best_move(card_piles_)
                moves.append(best_move)
                card_piles_[best_move.pile_id].append(best_move.card)
            return moves
        
        valid_moves = self.find_valid_moves(card_piles)
        valid_sequences = []
        for valid_move in valid_moves:
            # make a copy of the original card piiles
            card_piles_ = copy.deepcopy(card_piles)
            # make a valid move on one of the piles 
            card_piles_[valid_move.pile_id].append(valid_move.card)
            # remove card that was played from the players hand
            self.hand.remove(valid_move.card)
            next_move = self.find_best_move(card_piles_)
            valid_sequences.append([valid_move, next_move])
            # put the card back in the players hand
            self.hand.append(valid_move.card)
            
        return sorted(valid_sequences, key=lambda valid_sequence: sum([vm.increment for vm in valid_sequence]))[0]
        
        
    def find_best_move(self, card_piles: Dict[str, List[Card]]) -> Move:
        valid_moves = self.find_valid_moves(card_piles)
        return sorted(valid_moves, key=lambda valid_move: valid_move.increment)[0]
    
    def find_valid_moves(self, card_piles: Dict[str, List[Card]]) -> List[Move]:
        valid_moves = []
        for card in self.hand:
            for pile_id, pile in card_piles.items():
                move = Move(card, pile_id, pile[-1])
                if move.is_valid():
                    valid_moves.append(move)
                    
        return valid_moves
