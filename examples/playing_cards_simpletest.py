"""
Playing Cards Simple Test
"""

from board_config import display_drv
from displaybuf import DisplayBuffer
from mpdisplay import Events
from playing_cards import Cards


# If byte swapping is required and the display bus is capable of having byte swapping disabled,
# disable it and set a flag so we can swap the color bytes as they are created.
if display_drv.requires_byte_swap:
    needs_swap = display_drv.bus_swap_disable(True)
else:
    needs_swap = False

palette = display_drv.get_palette(name="wheel", swapped=needs_swap)

display_drv.rotation = 90
display = DisplayBuffer(display_drv)

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
