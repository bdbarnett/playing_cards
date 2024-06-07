"""
Playing Cards Simple Test
"""

from board_config import display_drv
from displaybuf import DisplayBuffer as SSD
from palettes import get_palette
from mpdisplay import Events
from playing_cards import Cards


display_drv.rotation = 90
ssd = SSD(display_drv, SSD.GS4_HMSB)

palette = get_palette(color_depth=4)
ssd.color_palette = palette

table_color = palette.GREEN

card_width = display_drv.width // 5
card_height = int(card_width * 7 / 5)

cards = Cards(card_width, card_height, palette, num_decks=1, table_color=table_color)

ssd.fill(table_color)
ssd.show()

def deal():
    ssd.fill(table_color)
    cards.shuffle()
    x = y = 0
    while len(cards) > 0:
        card = cards.draw_one()
        card.render(display, x, y)
        ssd.show()
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
                        ssd.show()
                        break


deal()
loop()
