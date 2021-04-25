from random import shuffle

from .card import Card

# Class representing a deck of cards
class Deck:

    # Initialize a deck of cards with symbols
    # greater than or equal to the given lowest
    # card
    # @param lowest_card
    #   Member of Card.SYMBOLS
    #   The lowest card in the deck
    def __init__(self, lowest_card=6):
        self.cards = []
        for suit in Card.SUITS:
            for symbol in Card.SYMBOLS:
                if symbol >= lowest_card:
                    self.cards.append(Card(suit, symbol))
    
    # Return the amount of cards in this deck
    def get_card_count(self):
        return len(self.cards)

    # Shuffle the deck
    def shuffle(self):
        shuffle(self.cards)
        
    #add a card to the bottom of the deck
    def add_card(self, card):
        self.cards.insert(0, card)

    # Insert cards at the top of the deck
    def insert_cards(self, cards):
        self.cards += cards

    # Test whether the deck is empty
    def is_empty(self):
        return self.get_card_count() == 0