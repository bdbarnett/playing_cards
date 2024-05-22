"""
This demo is written to use either DisplayBuf or Direct Draw.  To switch between them, comment out one
of the two import lines below.
"""

from displaybuf import DisplayBuffer

# from direct_draw import Graphics as Renderer

from board_config import display_drv
from mpdisplay import Events
from playing_cards import Cards


display_drv.rotation = 90
display = DisplayBuffer(display_drv)


palette = display_drv.get_palette()

table_color = palette.GREEN

card_width = display_drv.width // 5
card_height = int(card_width * 7 / 5)

cards = Cards(card_width, card_height, palette, num_decks=1, table_color=table_color)

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
                if event.button == 3:  # right-click
                    return  # exit loop
                x, y = event.pos
                for card in cards.in_play:
                    if card.hit_test(x, y):
                        card.flip()
                        display.show()
                        break


deal()
loop()
