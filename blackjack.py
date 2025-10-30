import random
from colorama import Fore, Style, init

#Setup
suits = ['Clubs', 'Spades', 'Diamonds', 'Hearts']
ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
card_symbols = {'Spades': '♠', 'Hearts': '♥', 'Clubs': '♣', 'Diamonds': '♦'}

values = {str(i): i for i in range(2, 11)}
values.update({'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11})


#Suggestion Logic
def suggest_move(player_score, dealer_card):
    """Very basic blackjack strategy suggestion."""
    dealer_value = values[dealer_card] if dealer_card in values else 10
    if player_score >= 17:
        return "Stand"
    elif player_score <= 11:
        return "Hit"
    elif dealer_value >= 7 and player_score < 17:
        return "Hit"
    else:
        return "Stand"


class Deck:
    def __init__(self):
        self.cards = [(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop() if self.cards else None


class Hand:
    def __init__(self, bet):
        self.cards = []
        self.bet = bet
        self.active = True

    def get_score(self):
        score = 0
        aces = 0
        for rank, _ in self.cards:
            score += values[rank]
            if rank == 'Ace':
                aces += 1
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def show(self, hide_first=False):
        if hide_first:
            print(f"{Fore.BLUE}[Hidden]{Style.RESET_ALL}, " +
                  ", ".join(f"{r}{card_symbols[s]} " for r, s in self.cards[1:]))
        else:
            cards_str = ", ".join(f"{r}{card_symbols[s]}" for r, s in self.cards)
            score_color = Fore.GREEN if self.get_score() <= 21 else Fore.RED
            print(f"Hand: {cards_str} "
                  f"(Score: {score_color}{self.get_score()}{Style.RESET_ALL}, "
                  f"Bet: ${self.bet})")


class Player:
    def __init__(self):
        self.balance = 500
        self.hands = []
        self.broke = False
        self.play_only_first = False

    def place_bets(self):
        self.hands = []
        print(f"\nYour current balance: ${self.balance}\n")
        num_hands = 0
        while num_hands < 1 or num_hands > 3:
            try:
                num_hands = int(input("How many hands do you want to play (1–3)? "))
            except ValueError:
                print("Enter a number between 1 and 3.")
                continue

        for i in range(num_hands):
            if self.balance <= 0:
                print("You have no money left to place another bet.")
                break

            try:
                bet = int(input(f"Enter bet for Hand {i+1} (max $500): "))
                if bet < 1:
                    print("You must bet at least $1.")
                    return
                elif bet > 500:
                    print("You can’t bet more than $500.")
                    return
                elif bet > self.balance:
                    print(f"You don't have enough money to bet ${bet}. Game over.")
                    self.broke = True
                    return
                else:
                    self.balance -= bet
                    self.hands.append(Hand(bet))
                    print(f"Bet ${bet} placed for Hand {i+1}. Remaining balance: ${self.balance}")
            except ValueError:
                print("Enter a valid number.")
                return

        if not self.hands:
            self.broke = True
            print("You have no active hands. Game over.")
        else:
            print()


class Dealer:
    def __init__(self):
        self.hand = Hand(0)


#Game Logic
def play_game():
    print(Fore.CYAN + "=== Welcome to Blackjack with Betting ===" + Style.RESET_ALL)
    player = Player()
    deck = Deck()

    while player.balance > 0:
        player.place_bets()
        if player.broke or not player.hands:
            break

        dealer = Dealer()
        deck = Deck()

        for _ in range(2):
            for hand in player.hands:
                hand.cards.append(deck.deal_card())
            dealer.hand.cards.append(deck.deal_card())

        print("\nDealer's Hand:")
        dealer.hand.show(hide_first=True)

        for i, hand in enumerate(player.hands, 1):
            print(f"\n--- Playing Hand {i} ---")
            hand.show()

            while hand.active:
                score = hand.get_score()
                if score > 21:
                    print(Fore.RED + "You busted!" + Style.RESET_ALL)
                    hand.active = False
                    break

                dealer_up_card = dealer.hand.cards[1][0]
                suggestion = suggest_move(score, dealer_up_card)
                print(Fore.YELLOW + f"(Suggestion: {suggestion})" + Style.RESET_ALL)

                action = input("Hit (H) or Stand (S)? ").strip().upper()
                if action == 'H':
                    new_card = deck.deal_card()
                    hand.cards.append(new_card)
                    print(f"You draw {new_card[0]}{card_symbols[new_card[1]]}.")
                    hand.show()
                elif action == 'S':
                    print(f"You stand with {score}.")
                    hand.active = False
                else:
                    print("Invalid choice. Enter H or S.")

            if player.play_only_first:
                print("\nYou went all-in on Hand 1. Skipping other hands...")
                break

        print("\nDealer’s turn:")
        dealer.hand.show()
        while dealer.hand.get_score() < 17:
            print("Dealer hits.")
            dealer.hand.cards.append(deck.deal_card())
            dealer.hand.show()

        dealer_score = dealer.hand.get_score()
        if dealer_score > 21:
            print(Fore.GREEN + "Dealer busts!" + Style.RESET_ALL)
        else:
            print(f"Dealer stands with {dealer_score}.")

        print("\n=== Round Results ===")
        for i, hand in enumerate(player.hands, 1):
            score = hand.get_score()
            if score > 21:
                print(Fore.RED + f"Hand {i}: You busted and lost ${hand.bet}." + Style.RESET_ALL)
            elif dealer_score > 21 or score > dealer_score:
                winnings = hand.bet * 2
                player.balance += winnings
                print(Fore.GREEN + f"Hand {i}: You win ${winnings}!" + Style.RESET_ALL)
            elif score == dealer_score:
                player.balance += hand.bet
                print(Fore.YELLOW + f"Hand {i}: Push. You get your ${hand.bet} back." + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Hand {i}: You lost ${hand.bet}." + Style.RESET_ALL)

        print(Fore.CYAN + f"\nYour balance: ${player.balance}" + Style.RESET_ALL)

        if player.balance == 0:
            print(Fore.RED + "You’re out of money. Game over!" + Style.RESET_ALL)
            break
        again = input("\nPlay another round? (Y/N): ").strip().upper()
        if again != 'Y':
            break

    print(Fore.MAGENTA + f"\nThanks for playing! Final balance: ${player.balance}" + Style.RESET_ALL)


if __name__ == "__main__":
    play_game()
