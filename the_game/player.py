from dataclasses import dataclass
from typing import (
    Dict,
    List,
)
from .card import Card


@dataclass
class Move:
    card: Card
    pile: str
    increment: int

    def __str__(self):
        return f'(Card: {self.card.value}, Pile: {self.pile}, Inc: {self.increment})'

    def __hash__(self):
        return hash(str(self))


class Player(object):

    def __init__(self, player_id: int):
        self.player_id = player_id
        self.hand = []

    def draw_cards(self, deck: List[Card], n: int = 1):
        for _ in range(n):
            self.hand.append(deck.draw())  # note this mutates deck "in place"

    def __repr__(self):
        return f"Player {self.player_id}: [{', '.join([str(card.value) for card in self.hand])}]"

    def make_move(self, card_piles: Dict[str, Card], min_cards: int=2):
        if min_cards == 1:
            valid_moves = self.find_valid_moves_first_pass(card_piles)
        else:
            valid_moves = find_valid_moves(card_piles)

        return evaluate_potential_moves(valid_moves)

    def evaluate_moves(self, moves: List[List[Move]]):
        move_total_increments = [
            sum([move.increment for move in move_list])
            for move_list in moves
        ]
        
        min_increment_index = move_total_increments.index(min(move_total_increments))
        return moves[min_increment_index]

    def find_valid_moves(self, card_piles: Dict[str, Card]):
        first_pass_valid_moves = self.find_valid_moves_first_pass(card_piles)
        return self.find_valid_sequences(first_pass_valid_moves)

    def find_valid_moves_first_pass(self, card_piles: Dict[str, Card]):
        valid_moves = []
        for card in self.hand:
            for pile_id, pile in card_piles.items():
                last_card = pile[-1]
                up_pile = 'up' in pile_id

                if check_valid_move(card, last_card, up_pile):
                    increment = calculate_increment(card, last_card, up_pile)
                    valid_moves.append(Move(card, pile_id, increment))

        return valid_moves

    def find_valid_sequences(self, valid_moves: List[Move]):
        """
        Two checks to find sequences
            1. Composed of two valid moves on different decks
            3. Composed of one valid move, then a move that's now valid
               this could happen if a -10 increment is played
        """
        valid_sequences = []

        move_sets = []
        for move_1 in valid_moves:
            for move_2 in valid_moves:
                if not (
                    move_1.card == move_2.card 
                    or {move_1, move_2} in move_sets
                    or move_1.pile == move_2.pile
                ):
                    valid_sequences.append([move_1, move_2])
                    move_sets.append({move_1, move_2})

        for valid_move in valid_moves:
            for card in self.hand:
                up_pile = 'up' in valid_move.pile
                if check_valid_move(card, valid_move.card, up_pile):
                   increment = calculate_increment(card, valid_move.card, up_pile) 
                   new_move = Move(card, valid_move.pile, increment)
                   valid_sequences.append([valid_move, new_move]) 

        return valid_sequences


def calculate_increment(new_card: Card, top_card: Card, up_pile: bool) -> int:
    increment = new_card - top_card    
    if not up_pile:
        increment *= -1

    return increment


def check_valid_move(card: Card, top_card: Card, up_pile: bool) -> bool:
    diff = card - top_card
    if diff == 0:
        # can't play the same card on itself, helpful for checking
        # if a move sequence is valid
        return False
    if up_pile and (diff > 0 or diff == -10):
        return True
    elif not up_pile and (diff < 0 or diff == 10):
        return True
    

def check_valid_move_pair(first_move: Move, second_move: Move):
    if first_move.pile != second_move.pile:
        return True
    
    up_pile_first_move = 'up' in first_move.pile
    return check_valid_move(second_move.card, first_move.card, up_pile_first_move)
