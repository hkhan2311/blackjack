import random
import time

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def value(self):
        if self.rank in ['Jack', 'Queen', 'King']:
            return 10
        elif self.rank == 'Ace':
            return 11
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        
    def build(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            self.build()
            self.shuffle()
            return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0
        
    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value()
        if card.rank == 'Ace':
            self.aces += 1
            
    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

class Player:
    def __init__(self, name, chips=100):
        self.name = name
        self.hand = Hand()
        self.chips = chips
        self.bet = 0
        self.standing = False
        
    def __str__(self):
        return f"{self.name} (Chips: {self.chips})"
    
    def place_bet(self, amount):
        if amount <= self.chips:
            self.bet = amount
            return True
        return False
    
    def hit(self, deck):
        self.hand.add_card(deck.deal())
        self.hand.adjust_for_ace()
        
    def stand(self):
        self.standing = True
        
    def bust(self):
        return self.hand.value > 21
    
    def has_blackjack(self):
        return len(self.hand.cards) == 2 and self.hand.value == 21
    
    def win(self):
        self.chips += self.bet
        self.bet = 0
        
    def lose(self):
        self.chips -= self.bet
        self.bet = 0
        
    def push(self):
        self.bet = 0

class BlackjackGame:
    def __init__(self, num_players=1):
        self.players = []
        self.dealer = Player("Dealer")
        self.deck = Deck()
        self.setup_players(num_players)
        
    def setup_players(self, num_players):
        for i in range(num_players):
            name = input(f"Enter player {i+1} name: ")
            self.players.append(Player(name))
            
    def deal_initial_cards(self):
        for _ in range(2):
            for player in self.players + [self.dealer]:
                player.hand.add_card(self.deck.deal())
                player.hand.adjust_for_ace()
    
    def show_hands(self, show_dealer=False):
        print("\nCurrent Hands:")
        if show_dealer:
            print(f"Dealer's hand: {', '.join(str(card) for card in self.dealer.hand.cards)} (Value: {self.dealer.hand.value})")
        else:
            print(f"Dealer's hand: {self.dealer.hand.cards[0]} and [hidden card]")
            
        for player in self.players:
            print(f"{player.name}'s hand: {', '.join(str(card) for card in player.hand.cards)} (Value: {player.hand.value})")
    
    def collect_bets(self):
        for player in self.players:
            while True:
                try:
                    bet = int(input(f"{player.name}, you have {player.chips} chips. How much would you like to bet? "))
                    if 0 < bet <= player.chips:
                        player.place_bet(bet)
                        break
                    else:
                        print("Invalid bet amount. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
    
    def player_turns(self):
        for player in self.players:
            print(f"\n{player.name}'s turn:")
            while not player.standing and not player.bust():
                self.show_hands()
                action = input("Would you like to (h)it or (s)tand? ").lower()
                if action == 'h':
                    player.hit(self.deck)
                    print(f"You drew: {player.hand.cards[-1]}")
                    if player.bust():
                        print(f"Bust! {player.name} loses {player.bet} chips.")
                        player.lose()
                elif action == 's':
                    player.stand()
                    print(f"{player.name} stands.")
                else:
                    print("Invalid input. Please enter 'h' or 's'.")
    
    def dealer_turn(self):
        print("\nDealer's turn:")
        self.show_hands(show_dealer=True)
        while self.dealer.hand.value < 17:
            time.sleep(1)
            self.dealer.hit(self.deck)
            print(f"Dealer hits and draws: {self.dealer.hand.cards[-1]}")
            self.show_hands(show_dealer=True)
            
        if self.dealer.bust():
            print("Dealer busts!")
        else:
            print("Dealer stands.")
    
    def determine_winners(self):
        dealer_value = self.dealer.hand.value
        dealer_bust = self.dealer.bust()
        
        for player in self.players:
            if player.bust():
                continue  # Player already lost when they busted
                
            player_value = player.hand.value
            
            if player.has_blackjack():
                if self.dealer.has_blackjack():
                    print(f"{player.name} pushes with blackjack. Bet returned.")
                    player.push()
                else:
                    print(f"{player.name} wins with blackjack! Pays 3:2")
                    player.chips += player.bet * 1.5  # Blackjack pays 3:2
                    player.bet = 0
            elif dealer_bust:
                print(f"{player.name} wins! Dealer busted.")
                player.win()
            elif player_value > dealer_value:
                print(f"{player.name} wins! {player_value} vs {dealer_value}")
                player.win()
            elif player_value == dealer_value:
                print(f"{player.name} pushes. {player_value} vs {dealer_value}")
                player.push()
            else:
                print(f"{player.name} loses. {player_value} vs {dealer_value}")
                player.lose()
    
    def reset_hands(self):
        for player in self.players + [self.dealer]:
            player.hand = Hand()
            player.standing = False
            player.bet = 0
    
    def play_round(self):
        print("\n" + "="*50)
        print("Starting new round!")
        print("="*50)
        
        self.deck = Deck()
        self.deck.shuffle()
        self.reset_hands()
        
        self.collect_bets()
        self.deal_initial_cards()
        self.show_hands()
        
        # Check for dealer blackjack
        if self.dealer.has_blackjack():
            print("\nDealer has blackjack!")
            self.show_hands(show_dealer=True)
            for player in self.players:
                if player.has_blackjack():
                    print(f"{player.name} also has blackjack. Push!")
                    player.push()
                else:
                    print(f"{player.name} loses.")
                    player.lose()
            return
        
        self.player_turns()
        self.dealer_turn()
        self.determine_winners()
    
    def play_game(self):
        while True:
            self.play_round()
            
            # Check if players want to continue
            active_players = [p for p in self.players if p.chips > 0]
            if not active_players:
                print("\nAll players are out of chips! Game over.")
                break
                
            self.players = active_players  # Remove players with no chips
            
            choice = input("\nWould you like to play another round? (y/n): ").lower()
            if choice != 'y':
                print("\nFinal chip counts:")
                for player in self.players:
                    print(f"{player.name}: {player.chips} chips")
                print("\nThanks for playing!")
                break

if __name__ == "__main__":
    print("Welcome to Blackjack!")
    while True:
        try:
            num_players = int(input("How many players? (1-4): "))
            if 1 <= num_players <= 4:
                break
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")
    
    game = BlackjackGame(num_players)
    game.play_game()
