"""
This demo is written to use either DisplayBuf or Direct Draw.  To switch between them, comment out one
of the two import lines below.
"""
from displaybuf import DisplayBuffer as Renderer
# from direct_draw import Graphics as Renderer

from board_config import display_drv
from mpdisplay import Events
from playing_cards import Cards


display_drv.rotation = 90
display = Renderer(display_drv)


class Pallette:
    def __init__(self, color_dict) -> None:
        self._color_dict = color_dict
        for name, color in color_dict.items():
            setattr(self, name, color)


pallette = Pallette({
    "BLACK": display.color(0x00, 0x00, 0x00),
    "BLUE": display.color(0x00, 0x00, 0xAA),
    "GREEN": display.color(0x00, 0xAA, 0x00),
    "CYAN": display.color(0x00, 0xAA, 0xAA),
    "RED": display.color(0xAA, 0x00, 0x00),
    "MAGENTA": display.color(0xAA, 0x00, 0xAA),
    "BROWN": display.color(0xAA, 0x55, 0x00),
    "LIGHTGRAY": display.color(0xAA, 0xAA, 0xAA),
    "DARKGRAY": display.color(0x55, 0x55, 0x55),
    "LIGHTGRAY": display.color(0x55, 0x55, 0xFF),
    "LIGHTGREEN": display.color(0x55, 0xFF, 0x55),
    "LIGHTCYAN": display.color(0x55, 0xFF, 0xFF),
    "LIGHTRED": display.color(0xFF, 0x55, 0x55),
    "LIGHTMAGENTA": display.color(0xFF, 0x55, 0xFF),
    "YELLOW": display.color(0xFF, 0xFF, 0x55),
    "WHITE": display.color(0xFF, 0xFF, 0xFF),
})

table_color = pallette.GREEN

card_width = display_drv.width // 5
card_height = int(card_width * 7/5)

cards = Cards(card_width, card_height, pallette, num_decks=1, table_color=table_color)

display.fill(table_color)
display.show()

def deal():
    display.fill(table_color)
    cards.shuffle()
    x = y = 0
    while len(cards) > 0:
        card = cards.draw_one()
        card.render(display, x, y)
        display.show()
        # x += cards.stack_offset_x
        x += cards.width
        if x + cards.width > display_drv.width:
            x = 0
            # y += cards.stack_offset_y
            y += cards.height
            if y + cards.height > display_drv.height:
                break

def loop():
    while True:
        if event := display_drv.poll():
            if event.type == Events.MOUSEBUTTONUP:
                if event.button == 3: # right-click
                    return  # exit loop
                x, y = event.pos
                for card in cards.in_play:
                    if card.hit_test(x, y):
                        card.flip()
                        display.show()
                        break


deal()
loop()
