import random

# fmt: off
# Define the deck of cards
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
values = { "Ace": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "Jack": 10, "Queen": 10, "King": 10}
# fmt: on

# Function to deal a card
def deal_card():
    suit = random.choice(suits)
    rank = random.choice(ranks)
    return (suit, rank)


# Function to calculate the total value of a hand
def calculate_hand_value(hand):
    value = 0
    num_aces = 0
    for card in hand:
        value += values[card[1]]
        if card[1] == "Ace":
            num_aces += 1
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    return value


# Function to play a hand
def play_hand():
    # Deal initial cards
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]

    # Player's turn
    while True:
        print("Player's hand:", player_hand)
        print("Dealer's hand:", [dealer_hand[0], ("", "Unknown")])
        choice = input("Choose an action: (P)lay or (S)top: ")
        if choice.lower() == "p":
            player_hand.append(deal_card())
            if calculate_hand_value(player_hand) > 21:
                print("Player busts! Dealer wins.")
                return
        elif choice.lower() == "s":
            break

    # Dealer's turn
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card())

    # Determine the winner
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    print("Player's total hand:", player_hand)
    print("Dealer's hand:", dealer_hand)
    print(f"{player_value=}, {dealer_value=}")
    if player_value > 21:
        print("Player busts! Dealer wins.")
    elif dealer_value > 21:
        print("Dealer busts! Player wins.")
    elif player_value > dealer_value:
        print("Player wins!")
    elif player_value < dealer_value:
        print("Dealer wins!")
    else:
        print("It's a tie!")
    print()


# Main game loop
while True:
    play_hand()
    choice = input("Do you want to play again? (Y/N): ")
    if choice.lower() != "y":
        break
