from board_config import display_drv
from mpdisplay import Events
from playing_cards import Cards
display_drv.rotation = 90

"""
This demo is written to use either DisplayBuf or TFT_Graphics.  To switch between them, comment out the
appropriate lines in the section below.
"""
#############################################
#
from displaybuf import DisplayBuffer as SSD
display = SSD(display_drv, SSD.RGB565)
color = display.color
show = display.show
#
#############################################
#
# from tft_graphics import Graphics
# display = Graphics(display_drv)
# color = display.color565
# show = lambda: None
#
#############################################

class Pallette:
    def __init__(self, color_dict) -> None:
        self._color_dict = color_dict
        for name, color in color_dict.items():
            setattr(self, name, color)


pallette = Pallette({
    "BLACK": color(0x00, 0x00, 0x00),
    "BLUE": color(0x00, 0x00, 0xAA),
    "GREEN": color(0x00, 0xAA, 0x00),
    "CYAN": color(0x00, 0xAA, 0xAA),
    "RED": color(0xAA, 0x00, 0x00),
    "MAGENTA": color(0xAA, 0x00, 0xAA),
    "BROWN": color(0xAA, 0x55, 0x00),
    "LIGHTGRAY": color(0xAA, 0xAA, 0xAA),
    "DARKGRAY": color(0x55, 0x55, 0x55),
    "LIGHTGRAY": color(0x55, 0x55, 0xFF),
    "LIGHTGREEN": color(0x55, 0xFF, 0x55),
    "LIGHTCYAN": color(0x55, 0xFF, 0xFF),
    "LIGHTRED": color(0xFF, 0x55, 0x55),
    "LIGHTMAGENTA": color(0xFF, 0x55, 0xFF),
    "YELLOW": color(0xFF, 0xFF, 0x55),
    "WHITE": color(0xFF, 0xFF, 0xFF),
})

table_color = pallette.GREEN

card_width = display_drv.width // 5
card_height = int(card_width * 7/5)

cards = Cards(card_width, card_height, pallette, num_decks=1, table_color=table_color)

display.fill(table_color)
show()

def deal():
    display.fill(table_color)
    cards.shuffle()
    x = y = 0
    while len(cards) > 0:
        card = cards.draw_one()
        card.render(display, x, y)
        show()
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
                        show()
                        break


deal()
loop()