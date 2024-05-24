"""
This demo is written to use either DisplayBuf or Direct Draw.  To switch between them, comment out one
of the two import lines below.
"""

from displaybuf import DisplayBuffer

# from direct_draw import Graphics as Renderer

from board_config import display_drv
from mpdisplay import Events
from playing_cards import Cards, Hand
from time import sleep

# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

if display_drv.height > display_drv.width:
    display_drv.rotation = 90
display = DisplayBuffer(display_drv)

palette = display_drv.get_palette(name="wheel", swapped=needs_swap)

# fmt: off
VALUES = { "Ace": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "Jack": 10, "Queen": 10, "King": 10}
# fmt: on


class Game(Cards):
    # override compare_rules and/or compare method if desired
    def __init__(self, target, palette):

        card_width = display_drv.width // 5
        card_height = int(card_width * 7 / 5)
        super().__init__(card_width, card_height, palette)
        self.show = target.show if hasattr(target, "show") else lambda: None
        self.dealer = Hand(
            True,
            target=target,
            start_x=0,
            start_y=0,
            top_card_hidden=True,
            other_cards_hidden=False,
            layout_horizontal=True,
            layout_direction=1,
            layout_offset=self.width,
        )
        self.player1 = Hand(
            False,
            target=target,
            start_x=0,
            start_y=target.height - self.height,
            top_card_hidden=False,
            other_cards_hidden=False,
            layout_horizontal=True,
            layout_direction=1,
            layout_offset=self.width,
        )
        self._target = target
        target.fill(self._table_color)
        self.button1 = Button(
            10,
            (target.height - 20) // 2,
            50,
            20,
            palette.GREY,
            "Play",
            palette.BLACK,
            target,
        )
        self.button2 = Button(
            target.width - 60,
            (target.height - 20) // 2,
            50,
            20,
            palette.GREY,
            "Exit",
            palette.BLACK,
            target,
        )
        self.show()
        self.loop()

    def reset(self):
        self._target.fill_rect(
            self.button1.x + self.button1.width,
            self.button1.y,
            self.button2.x - self.button1.x - self.button1.width,
            self.button1.height * 2,
            self._table_color,
        )
        self.clear_table()
        self.player1.clear()
        self.dealer.clear()
        self.shuffle()

    # Function to calculate the total value of a hand
    @staticmethod
    def calculate_hand_value(hand):
        value = 0
        num_aces = 0
        for card in hand:
            value += VALUES[card.rank]
            if card.rank == "Ace":
                num_aces += 1
        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1
        return value

    def poll(self):
        ret = None
        if event := display_drv.poll():
            if event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                for button in [self.button1, self.button2]:
                    if button.hit_test(x, y):
                        ret = button.text.lower()
        return ret

    def loop(self):
        while True:
            if event := display_drv.poll():
                if event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if self.button1.hit_test(x, y):
                        self.play_hand()
                        self.button1.text = "Play"
                        self.button2.text = "Exit"
                        self.show()
                    elif self.button2.hit_test(x, y):
                        return

    def play_hand(self):
        self.reset()
        self.button1.text = "Hit"
        self.button2.text = "Stand"
        self.player1.place(self.draw_one())
        self.show()
        self.dealer.place(self.draw_one())
        self.show()
        self.player1.place(self.draw_one())
        self.show()
        self.dealer.place(self.draw_one(), top_card=True)
        self.show()

        # Player's turn
        while True:
            if choice := self.poll():
                if choice == "hit":
                    self.player1.place(self.draw_one())
                    self.show()
                    if self.calculate_hand_value(self.player1.in_pile) > 21:
                        self.dealer.reveal()
                        text = "Player busts!\nDealer wins."
                        self.print_message(text, self._palette.RED)
                        return
                elif choice == "stand":
                    break

        # Dealer's turn
        self.dealer.reveal()
        self.show()
        while self.calculate_hand_value(self.dealer.in_pile) < 17:
            self.dealer.place(self.draw_one())
            self.show()

        # Determine the winner
        player_value = self.calculate_hand_value(self.player1.in_pile)
        dealer_value = self.calculate_hand_value(self.dealer.in_pile)
        # print("Player's total hand:", self.player1.in_pile)
        # print("Dealer's hand:", self.dealer.in_pile)
        # print(f"{player_value=}, {dealer_value=}")
        if player_value > 21:
            text = "Player busts!\nDealer wins."
        elif dealer_value > 21:
            text = "Dealer busts!\nPlayer wins."
        elif player_value > dealer_value:
            text = "Player wins!"
        elif player_value < dealer_value:
            text = "Dealer wins!"
        else:
            text = "It's a tie!"
        self.print_message(text, self._palette.RED)
        # print(text, "\n")

    def print_message(self, text, color):
        self._target.btext(
            text,
            (self._target.width - self._target.bfont_width() * len(text.split("\n")[0]))
            // 2,
            (self._target.height - self._target.bfont_height()) // 2,
            color,
        )


class Button:
    def __init__(self, x, y, width, height, color, text, text_color, target):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = min(width, height) // 4
        self.color = color
        self.text_color = text_color
        self.target = target
        self.text = text

    def draw(self, pressed=False):
        self.target.btext(
            " ", 0, 0, 0x0
        )  # Initialize the font so we can get the width and height
        color = self.color if not pressed else ~self.color & 0xFFFF
        self.target.roundrect(
            self.x, self.y, self.width, self.height, self.radius, color, True
        )
        self.target.btext(
            self.text,
            self.x + (self.width - self.target.bfont_width() * len(self.text)) // 2,
            self.y + (self.height - self.target.bfont_height()) // 2,
            self.text_color,
        )

    def hit_test(self, x, y):
        pressed = (
            self.x <= x < self.x + self.width and self.y <= y < self.y + self.height
        )
        if pressed:
            self.draw(True)
            sleep(0.25)
            self.draw()
        return pressed

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.draw()


game = Game(display, palette)
