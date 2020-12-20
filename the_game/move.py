from .card import Card


class Move:
    def __init__(self, card: Card, pile_id: str, top_card: Card):
        self.card = card
        self.pile_id = pile_id
        self.top_card = top_card
        self.count_up_pile = 'up' in self.pile_id
        self.increment = (self.card - self.top_card) * (1 if self.count_up_pile else -1)

    def __str__(self) -> str:
        return f'(Card: {self.card.value}, Pile: {self.pile_id}, Inc: {self.increment})'
    
    def __eq__(self, other: Card) -> bool:
        if (
            self.card == other.card
            and self.pile_id == other.pile_id
            and self.increment == other.increment
            and self.top_card == other.top_card
        ):
            return True

        return False

    def __hash__(self):
        return hash(str(self))
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def is_valid(self):
        diff = self.card - self.top_card
        if self.increment == 0:
            return False
        
        if self.count_up_pile and (diff > 0 or diff == -10):
            return True
        
        if not self.count_up_pile and (diff < 0 or diff == 10):
            return True
        
        return False
