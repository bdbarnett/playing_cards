# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
playing_cards.py - A simple playing card library for MPDisplay.
Cards can be rendered to FrameBuf_Plus, DisplayBuffer or TFT_Graphics targets.
"""

import random


HEARTS = "Hearts"
DIAMONDS = "Diamonds"
CLUBS = "Clubs"
SPADES = "Spades"
SUITS = [HEARTS, DIAMONDS, CLUBS, SPADES]

ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING = \
    "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"
NAMES = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING]


class Cards:

    _positions = {
        "Ace": [(2, 3)],
        "2": [(2, 0), (2, 6)],
        "3": [(2, 0), (2, 3), (2, 6)],
        "4": [(1, 0), (3, 0), (1, 6), (3, 6)],
        "5": [(1, 0), (3, 0), (2, 3), (1, 6), (3, 6)],
        "6": [(1, 0), (3, 0), (1, 3), (3, 3), (1, 6), (3, 6)],
        "7": [(1, 0), (3, 0), (1, 3), (2, 1), (3, 3), (1, 6), (3, 6)],
        "8": [(1, 0), (3, 0), (1, 3), (2, 1), (2, 5), (3, 3), (1, 6), (3, 6)],
        "9": [(1, 0), (3, 0), (1, 2), (3, 2), (2, 3), (1, 4), (3, 4), (1, 6), (3, 6)],
        "10": [(1, 0), (3, 0), (1, 2), (3, 2), (2, 1), (2, 5), (1, 4), (3, 4), (1, 6), (3, 6)],
        "Jack": [],
        "Queen": [],
        "King": [],
    }

    _suit_glyphs = {
        HEARTS: chr(0x03),  # '♥'
        DIAMONDS: chr(0x04),  # '♦'
        CLUBS: chr(0x05),  # '♣'
        SPADES: chr(0x06),  # '♠'
    }

    def __init__(self, width, height, pallette, num_decks=1, table_color=None, suits=SUITS, names=NAMES):
        self.set_dimensions(width, height)
        self._pallette = pallette
        self._num_decks = num_decks
        self._table_color = table_color if table_color is not None else pallette.GREEN
        self._suits = suits
        self._names = names
        self._back_color = pallette.BLUE
        self._border_color = pallette.BLACK
        self._bg_color = pallette.WHITE

        self._suit_colors = {
            HEARTS: pallette.RED,
            DIAMONDS: pallette.RED,
            CLUBS: pallette.BLACK,
            SPADES: pallette.BLACK,
        }

        self._all_cards = set(Card(suit, name, self) for suit in self._suits for name in self._names for _ in range(num_decks))
        self._in_chute = set()
        self._in_play = set()
        self._in_discard = set()
        self.shuffle()

    def set_dimensions(self, width, height):
        self._sfw = 8   # Small font width
        self._sfh = 16   # Small font height
        self._lfs = 2  # Large font scale
        self._lfw = 8  # Large font width
        self._lfh = 16  # Large font height
        self._fcs = 6  # Face card scale
        self._width = width  # Width of card including padding
        self._height = height  # Height of card including padding
        self._stack_offset_x = width // 5  # Amount of space to leave between cards stacked horizontally
        self._stack_offset_y = height // 4  # Amount of space to leave between cards stacked vertically
        self._draw_width = width * 9 // 10  # Width of card excluding padding
        self._draw_height = height * 9 // 10  # Height of card excluding padding
        self._x_offset = width // 20  # Offset from left edge of card to start drawing
        self._y_offset = height // 20  # Offset from top edge of card to start drawing
        self._radius = width // 10  # Radius of rounded corners

        # These are the positions of the suit glyphs and card values on the card
        self._x_positions = [i * self._draw_width // 10 for i in range(1, 10, 2)]
        self._y_positions = [i * self._draw_height // 10 for i in range(1, 10, 2)]
        self._y_positions.extend([self._y_positions[0] + i * ((self._y_positions[4] - self._y_positions[0]) // 3) for i in range(1, 3)])
        self._y_positions.sort()

    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    @property
    def stack_offset_x(self):
        return self._stack_offset_x
    
    @property
    def stack_offset_y(self):
        return self._stack_offset_y

    @property
    def in_chute(self):
        return list(self._in_chute)
    
    @property
    def in_play(self):
        return list(self._in_play)
    
    @property
    def in_discard(self):
        return list(self._in_discard)
    
    @property
    def all_cards(self):
        return list(self._all_cards)

    def __len__(self):
        return len(self._in_chute)

    def shuffle(self):
        # Move all cards back into the deck
        self._in_chute = set(card for card in self._all_cards)
        self._in_play.clear()
        self._in_discard.clear()
    
    def discard(self, card):
        self._in_play.remove(card)
        self._in_discard.add(card)

    def draw_one(self):
        if self._in_chute:
            card = random.choice(list(self._in_chute))
            self._in_chute.remove(card)
            self._in_play.add(card)
            return card
        else:
            raise ValueError("No cards left in the chute")

    def draw(self, quantity=1):
        return [self.draw_one() for _ in range(quantity)]

    def erase(self, target, x, y):
        draw_x = x + self._x_offset
        draw_y = y + self._y_offset

        target.fill_rect(draw_x, draw_y, self._draw_width+1, self._draw_height+1, self._table_color)

    def render(self, card, target, x, y, hidden=True):
        draw_x = x + self._x_offset
        draw_y = y + self._y_offset

        # Save the state of the card
        card.set_state(target, x, y, hidden)

        # Draw the card background
        target.roundrect(draw_x, draw_y, self._draw_width, self._draw_height, self._radius, self._bg_color, True)

        # Draw the card border
        target.roundrect(draw_x, draw_y, self._draw_width, self._draw_height, self._radius, self._border_color, False)

        if hidden:
            # Draw the card back
            target.roundrect(draw_x+2, draw_y+2, self._draw_width-4, self._draw_height-4, self._radius, self._back_color, True)
            return

        # Draw the card value in the top left corner
        target.btext(
            card.value,
            draw_x + self._x_positions[0] - len(card.value) * self._lfw // 2,
            draw_y + self._y_positions[0] - self._lfh // 2,
            self._suit_colors[card.suit],
        )

        # Draw the card value in the bottom right corner
        target.btext(
            card.value,
            draw_x + self._x_positions[4] - len(card.value) * self._lfw // 2,
            draw_y + self._y_positions[6] - self._lfh // 2,
            self._suit_colors[card.suit],
            inverted=True,
        )

        # Draw the suit glyph in the top left corner
        target.btext(
            self._suit_glyphs[card.suit],
            draw_x + self._x_positions[0] - self._sfw // 2,
            draw_y + self._y_positions[0] + self._lfh // 2,
            self._suit_colors[card.suit]
        )

        # Draw the suit glyph in the bottom right corner
        target.btext(
            self._suit_glyphs[card.suit],
            draw_x + self._x_positions[4] - self._sfw // 2,
            draw_y + self._y_positions[6] - self._lfh - self._sfh // 2,
            self._suit_colors[card.suit],
            inverted=True,
        )

        # Draw the suit glyph on the grid (on Ace through 10)
        for x_pos, y_pos in self._positions[card.name]:
            target.btext(
                self._suit_glyphs[card.suit],
                draw_x + self._x_positions[x_pos] - self._lfs * self._lfw // 2,
                draw_y + self._y_positions[y_pos] - self._lfs * self._lfh // 2,
                self._suit_colors[card.suit],
                scale=self._lfs,
                inverted = y_pos > 3,
            )

        # Draw a large letter on face cards instead of a graphic
        if card.name in ["Jack", "Queen", "King"]:
            target.btext(
                card.value[0],
                draw_x + self._x_positions[2] - self._fcs * self._lfw // 2,
                draw_y + self._y_positions[3] - self._fcs * self._lfh // 2,
                self._suit_colors[card.suit],
                scale=self._fcs,
            )


class Card:
    def __init__(self, suit, name, chute):
        self._suit = suit
        self._name = name
        self._chute = chute
        self._hidden = False
        self._position = None
        self._target = None

    def __str__(self):
        return f"{self.name} of {self.suit}"

    def __repr__(self):
        return f"{self.name} of {self.suit}"

    @property
    def target(self):
        return self._target
    
    @target.setter
    def target(self, value):
        self._target = value

    @property
    def value(self):
        return self.name if len(self.name) < 3 else self.name[0]

    @property
    def suit(self):
        return self._suit
    
    @property
    def name(self):
        return self._name

    @property
    def hidden(self):
        return self._hidden
    
    @hidden.setter
    def hidden(self, value):
        self.render(self._target, self.position[0], self.position[1], hidden=value)

    def hide(self):
        self.hidden = True

    def reveal(self):
        self.hidden = False

    def flip(self):
        self.hidden = not self.hidden

    def discard(self):
        self._chute.discard(self)

    def erase(self):
        self._chute.erase(self._target, self.position[0], self.position[1])

    def hit_test(self, x, y):
        if self.position is None:
            return False
        return self.position[0] <= x < self.position[0] + self._chute.width and self.position[1] <= y < self.position[1] + self._chute.height

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value

    def render(self, target, x, y, hidden=True):
        self._chute.render(self, target, x, y, hidden=hidden)

    def set_state(self, target, x, y, hidden):
        self._target = target
        self._position = (x, y)
        self._hidden = hidden
