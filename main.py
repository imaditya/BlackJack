import os
import sys
from collections import defaultdict

# ANSI Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @staticmethod
    def colorize(text, color):
        return f"{color}{text}{Colors.END}"

class BlackjackGame:
    def __init__(self):
        self.total_decks = int(input("Enter the total number of decks: "))
        self.num_players = int(input("Enter the number of players (including yourself): "))
        self.player_names = []
        
        # Auto-generate player names
        for i in range(self.num_players):
            self.player_names.append(f"Player {i + 1}")
        
        self.omega_ii = {
            '2': 1, '3': 1, '4': 2, '5': 2, '6': 2,
            '7': 1, '8': 0, '9': -1, '10': -2,
            'J': -2, 'Q': -2, 'K': -2, 'A': 0
        }
        self.reset_game()
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.deck = self.create_deck()
        self.cards_dealt = []
        self.running_count = 0
        self.player_balance = 1000
        self.current_bet = 1
        self.round_number = 0
        self.game_history = []
        
        # Initialize player hands for each round
        self.player_hands = {}
        self.player_results = {}
        for name in self.player_names:
            self.player_hands[name] = []
            self.player_results[name] = "active"
        
    def create_deck(self):
        """Create a deck with the specified number of decks"""
        cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = {}
        for card in cards:
            deck[card] = 4 * self.total_decks
        return deck
    
    def add_card_to_dealt(self, card):
        """Add a card to the dealt cards and update running count"""
        if card in self.deck and self.deck[card] > 0:
            self.deck[card] -= 1
            self.cards_dealt.append(card)
            self.running_count += self.omega_ii[card]
            self.game_history.append(('card_dealt', card))
            return True
        return False
    
    def undo_last_action(self):
        """Undo the last card entry (up to 5 moves)"""
        if self.game_history:
            last_action = self.game_history.pop()
            if last_action[0] == 'card_dealt':
                card = last_action[1]
                self.deck[card] += 1
                self.cards_dealt.remove(card)
                self.running_count -= self.omega_ii[card]
                print(f"Undid last card: {card}")
                
                # Provide context about what needs to be re-entered
                cards_dealt_count = len(self.cards_dealt)
                num_players = self.num_players
                
                if cards_dealt_count < num_players:
                    # We're in first card dealing phase
                    player_num = cards_dealt_count + 1
                    print(f"⚠️  You need to re-enter Player {player_num}'s first card")
                elif cards_dealt_count == num_players:
                    # We just undid the dealer's upcard
                    print(f"⚠️  You need to re-enter the dealer's upcard")
                elif cards_dealt_count < (num_players * 2 + 1):
                    # We're in second card dealing phase
                    second_card_index = cards_dealt_count - num_players - 1
                    player_num = second_card_index + 1
                    print(f"⚠️  You need to re-enter Player {player_num}'s second card")
                else:
                    print(f"⚠️  Card undone during gameplay")
                
                return True
        print("Nothing to undo")
        return False
    
    def undo_multiple_moves(self):
        """Undo multiple moves (up to 5)"""
        if not self.game_history:
            print("Nothing to undo")
            return
        
        max_undo = min(5, len(self.game_history))
        print(f"Available moves to undo: {max_undo}")
        
        try:
            num_moves = int(input(f"How many moves to undo? (1-{max_undo}): "))
            if 1 <= num_moves <= max_undo:
                for _ in range(num_moves):
                    if self.game_history:
                        last_action = self.game_history.pop()
                        if last_action[0] == 'card_dealt':
                            card = last_action[1]
                            self.deck[card] += 1
                            self.cards_dealt.remove(card)
                            self.running_count -= self.omega_ii[card]
                print(f"Undid {num_moves} moves")
            else:
                print("Invalid number of moves")
        except ValueError:
            print("Invalid input")
    
    def get_true_count(self):
        """Calculate true count based on remaining decks"""
        cards_remaining = sum(self.deck.values())
        decks_remaining = cards_remaining / 52
        if decks_remaining <= 0:
            return 0
        return round(self.running_count / decks_remaining, 2)
    
    def get_deck_penetration(self):
        """Calculate deck penetration percentage"""
        total_cards = 52 * self.total_decks
        cards_dealt = len(self.cards_dealt)
        return (cards_dealt / total_cards) * 100
    
    def display_omega_board(self):
        """Display probability board sorted by highest to lowest with card chances"""
        print("\n" + "="*80)
        print("OMEGA BOARD - Card Probabilities")
        print("="*80)
        
        total_remaining = sum(self.deck.values())
        if total_remaining == 0:
            print("No cards remaining!")
            return
        
        probabilities = []
        for card in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
            count = self.deck[card]
            prob = (count / total_remaining) * 100
            probabilities.append((card, count, prob))
        
        # Sort by probability (highest first)
        probabilities.sort(key=lambda x: x[2], reverse=True)
        
        # Display in two columns
        print("Card Probabilities:".ljust(40) + "1-in-X Chances:")
        print("-" * 40 + " " + "-" * 39)
        
        for card, count, prob in probabilities:
            # Calculate 1-in-X chance
            if prob > 0:
                one_in_x = round(100 / prob, 1)
                chance_text = f"1 in {one_in_x}"
            else:
                chance_text = "No cards left"
            
            left_side = f"{card:>2}: {count:>2} cards ({prob:>5.1f}%)"
            right_side = f"{card}: {chance_text}"
            print(f"{left_side:<40} {right_side}")
        
        print(f"\nTotal remaining cards: {total_remaining}")
        print(f"Deck penetration: {self.get_deck_penetration():.1f}%")
        
        if self.get_deck_penetration() >= 70:
            print("⚠️ Deck penetration reached 70% — recommend ending this session.")
    
    def calculate_hand_value(self, cards):
        """Calculate the value of a hand"""
        total = 0
        aces = 0
        
        for card in cards:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card == 'A':
                aces += 1
                total += 11
            else:
                total += int(card)
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_soft_hand(self, cards):
        """Check if hand is soft (contains ace counted as 11)"""
        total = 0
        aces = 0
        
        for card in cards:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card == 'A':
                aces += 1
                total += 11
            else:
                total += int(card)
        
        return total <= 21 and aces > 0
    
    def get_basic_strategy(self, player_cards, dealer_upcard, can_double=True, can_split=False):
        """Get basic strategy recommendation with Omega II adjustments"""
        player_total = self.calculate_hand_value(player_cards)
        dealer_value = 10 if dealer_upcard in ['J', 'Q', 'K'] else (11 if dealer_upcard == 'A' else int(dealer_upcard))
        true_count = self.get_true_count()
        
        # Check for pair splitting
        if can_split and len(player_cards) == 2 and player_cards[0] == player_cards[1]:
            if player_cards[0] in ['A', '8']:
                return "SPLIT", Colors.PURPLE
            elif player_cards[0] in ['2', '3', '6', '7'] and dealer_value <= 7:
                return "SPLIT", Colors.PURPLE
            elif player_cards[0] == '4' and dealer_value in [5, 6]:
                return "SPLIT", Colors.PURPLE
            elif player_cards[0] == '5':
                # Never split 5s, treat as 10
                pass
            elif player_cards[0] == '9' and dealer_value not in [7, 10, 11]:
                return "SPLIT", Colors.PURPLE
            elif player_cards[0] == '10':
                # Never split 10s unless very high count
                if true_count >= 5 and dealer_value in [5, 6]:
                    return "SPLIT", Colors.PURPLE
        
        # Soft hands (with Ace)
        if self.is_soft_hand(player_cards):
            if player_total >= 19:
                return "STAND", Colors.ORANGE
            elif player_total == 18:
                if dealer_value in [2, 7, 8]:
                    return "STAND", Colors.ORANGE
                elif dealer_value in [3, 4, 5, 6] and can_double:
                    return "DOUBLE", Colors.GREEN
                else:
                    return "HIT", Colors.RED
            elif player_total in [17, 16] and dealer_value in [3, 4, 5, 6] and can_double:
                return "DOUBLE", Colors.GREEN
            elif player_total in [15, 14] and dealer_value in [4, 5, 6] and can_double:
                return "DOUBLE", Colors.GREEN
            elif player_total == 13 and dealer_value in [5, 6] and can_double:
                return "DOUBLE", Colors.GREEN
            else:
                return "HIT", Colors.RED
        
        # Hard hands with Omega II deviations
        if player_total >= 17:
            return "STAND", Colors.ORANGE
        elif player_total == 16:
            if dealer_value >= 7:
                # Omega II deviation: Stand 16 vs 10 when TC >= +0
                if dealer_value == 10 and true_count >= 0:
                    return "STAND", Colors.ORANGE
                # Stand 16 vs 9 when TC >= +5
                elif dealer_value == 9 and true_count >= 5:
                    return "STAND", Colors.ORANGE
                return "HIT", Colors.RED
            else:
                return "STAND", Colors.ORANGE
        elif player_total == 15:
            if dealer_value >= 7:
                # Stand 15 vs 10 when TC >= +4
                if dealer_value == 10 and true_count >= 4:
                    return "STAND", Colors.ORANGE
                return "HIT", Colors.RED
            else:
                return "STAND", Colors.ORANGE
        elif player_total in [13, 14]:
            if dealer_value >= 7:
                return "HIT", Colors.RED
            else:
                return "STAND", Colors.ORANGE
        elif player_total == 12:
            if dealer_value in [2, 3]:
                # Hit 12 vs 2 when TC < +3, vs 3 when TC < +2
                if dealer_value == 2 and true_count < 3:
                    return "HIT", Colors.RED
                elif dealer_value == 3 and true_count < 2:
                    return "HIT", Colors.RED
                else:
                    return "STAND", Colors.ORANGE
            elif dealer_value >= 7:
                return "HIT", Colors.RED
            else:
                return "STAND", Colors.ORANGE
        elif player_total == 11:
            if can_double:
                # Don't double 11 vs A when TC < +1
                if dealer_value == 11 and true_count < 1:
                    return "HIT", Colors.RED
                return "DOUBLE", Colors.GREEN
            else:
                return "HIT", Colors.RED
        elif player_total == 10:
            if dealer_value <= 9 and can_double:
                # Don't double 10 vs 10 when TC < +4
                if dealer_value == 10 and true_count < 4:
                    return "HIT", Colors.RED
                return "DOUBLE", Colors.GREEN
            else:
                return "HIT", Colors.RED
        elif player_total == 9:
            if dealer_value in [3, 4, 5, 6] and can_double:
                return "DOUBLE", Colors.GREEN
            else:
                return "HIT", Colors.RED
        else:
            return "HIT", Colors.RED
    
    def get_bet_amount(self):
        """Calculate bet based on true count using proper Omega II strategy"""
        true_count = self.get_true_count()
        
        # Omega II betting strategy - more aggressive than basic systems
        if true_count <= 0:
            return 1  # Minimum bet for negative counts
        elif true_count <= 1:
            return 1  # Still minimum for low positive counts
        elif true_count <= 2:
            return 2  # 2 units at TC +2
        elif true_count <= 3:
            return 4  # 4 units at TC +3
        elif true_count <= 4:
            return 6  # 6 units at TC +4
        elif true_count <= 5:
            return 8  # 8 units at TC +5
        else:
            return min(10, self.player_balance // 20)  # Cap at 10 units or 5% of balance
    
    def get_wonging_status(self):
        """Provide wonging recommendation"""
        true_count = self.get_true_count()
        
        if true_count >= 2:
            return "STAY - Favorable count detected!"
        elif true_count >= 0:
            return "NEUTRAL - Acceptable conditions"
        else:
            return "CONSIDER EXIT - Unfavorable count"
    
    def get_card_input(self, prompt):
        """Get card input with validation"""
        valid_cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        original_prompt = prompt
        while True:
            card = input(prompt).upper().strip()
            
            if card == 'RESTART':
                return card
            elif card == 'UNDO':
                # Handle undo directly here instead of bubbling up
                if self.undo_last_action():
                    print("Please continue from where the undo occurred (not from the current prompt).")
                    prompt = f"Re-enter the appropriate card - {original_prompt}"
                    continue
                else:
                    print("Nothing to undo.")
                    prompt = f"Please enter a card - {original_prompt}"
                    continue
            elif card == 'UNDO+':
                # Handle multiple undo directly here
                self.undo_multiple_moves()
                print("Please continue from where the undos occurred (not from the current prompt).")
                prompt = f"Re-enter the appropriate card - {original_prompt}"
                continue
            
            # Normalize card input - handle alternative formats
            if card == '1':
                card = 'A'  # Allow 1 for Ace
            elif card in ['J', 'Q', 'K']:
                card = card.upper()  # Ensure uppercase for face cards
            
            if card in valid_cards:
                if self.deck[card] > 0:
                    return card
                else:
                    print(f"No more {card}s in deck!")
                    # Reset prompt back to original after error
                    prompt = original_prompt
            else:
                print("Invalid card. Enter: A/1, 2-10, J, Q, K (or 'restart', 'undo', 'undo+' for multiple undo)")
                # Reset prompt back to original after error
                prompt = original_prompt
    
    def play_hand(self, player_cards, dealer_upcard, hand_name=""):
        """Play a single hand"""
        print(f"\n{hand_name}Player cards: {player_cards} (Value: {self.calculate_hand_value(player_cards)})")
        print(f"Dealer upcard: {dealer_upcard}")
        
        # Check for blackjack
        if len(player_cards) == 2 and self.calculate_hand_value(player_cards) == 21:
            print("BLACKJACK!")
            return player_cards, "blackjack"
        
        can_double = len(player_cards) == 2
        can_split = len(player_cards) == 2 and player_cards[0] == player_cards[1]
        
        while True:
            player_total = self.calculate_hand_value(player_cards)
            
            if player_total > 21:
                print("BUST!")
                return player_cards, "bust"
            
            # Get strategy recommendation
            action, color = self.get_basic_strategy(player_cards, dealer_upcard, can_double, can_split)
            
            # Display count information and recommendation
            remaining_decks = sum(self.deck.values()) / 52
            print(f"\n{'='*50}")
            print(f"OMEGA II COUNT INFO:")
            print(f"Running Count: {self.running_count}")
            print(f"Remaining Decks: {remaining_decks:.1f}")
            print(f"True Count: {self.get_true_count()}")
            print(f"{'='*50}")
            print(f"Recommended action: {Colors.colorize(action, color)}")
            print(f"{'='*50}")
            
            # Get player action
            actions = ["hit", "stand"]
            if can_double:
                actions.append("double")
            if can_split:
                actions.append("split")
            
            print(f"Available actions: {', '.join(actions)}")
            choice = input("Your choice (hit-h, stand-s, double-d, split-p): ").lower().strip()
            
            # Normalize action input - handle single letters and full words
            if choice in ['h', 'hit']:
                choice = "hit"
            elif choice in ['s', 'stand']:
                choice = "stand"
            elif choice in ['d', 'double']:
                choice = "double"
            elif choice in ['p', 'split']:
                choice = "split"
            elif choice in ['restart']:
                return player_cards, choice
            
            if choice == "hit":
                card = self.get_card_input("Enter card received: ")
                if card == 'RESTART':
                    return player_cards, card.lower()
                
                if self.add_card_to_dealt(card):
                    player_cards.append(card)
                    can_double = False
                    can_split = False
                    print(f"Player cards: {player_cards} (Value: {self.calculate_hand_value(player_cards)})")
                
            elif choice == "stand":
                return player_cards, "stand"
                
            elif choice == "double" and can_double:
                card = self.get_card_input("Enter card received: ")
                if card == 'RESTART':
                    return player_cards, card.lower()
                
                if self.add_card_to_dealt(card):
                    player_cards.append(card)
                    print(f"Player cards: {player_cards} (Value: {self.calculate_hand_value(player_cards)})")
                    return player_cards, "double"
                
            elif choice == "split" and can_split:
                return player_cards, "split"
                
            else:
                print("Invalid choice. Use: h/hit, s/stand, d/double, p/split")
    
    def play_dealer_hand(self, dealer_cards):
        """Play dealer's hand following soft 17 rule"""
        print(f"\nDealer's turn:")
        print(f"Dealer cards: {dealer_cards} (Value: {self.calculate_hand_value(dealer_cards)})")
        
        while True:
            dealer_total = self.calculate_hand_value(dealer_cards)
            
            if dealer_total > 21:
                print("Dealer BUST!")
                break
            
            # Dealer hits on soft 17
            if dealer_total < 17 or (dealer_total == 17 and self.is_soft_hand(dealer_cards)):
                card = self.get_card_input("Enter dealer's next card: ")
                if card == 'RESTART':
                    return dealer_cards, card.lower()
                
                if self.add_card_to_dealt(card):
                    dealer_cards.append(card)
                    print(f"Dealer cards: {dealer_cards} (Value: {self.calculate_hand_value(dealer_cards)})")
            else:
                print("Dealer stands.")
                break
        
        return dealer_cards, "complete"
    
    def determine_winner(self, player_cards, dealer_cards, player_action):
        """Determine the winner of a hand"""
        player_total = self.calculate_hand_value(player_cards)
        dealer_total = self.calculate_hand_value(dealer_cards)
        
        if player_action == "blackjack":
            if len(dealer_cards) == 2 and dealer_total == 21:
                return "push"
            return "blackjack"
        
        if player_total > 21:
            return "dealer"
        
        if dealer_total > 21:
            return "player"
        
        if player_total > dealer_total:
            return "player"
        elif dealer_total > player_total:
            return "dealer"
        else:
            return "push"
    
    def play_round(self):
        """Play a complete round with multiple players"""
        self.round_number += 1
        remaining_decks = sum(self.deck.values()) / 52
        
        print(f"\n{'='*60}")
        print(f"ROUND {self.round_number}")
        print(f"Balance: ${self.player_balance}")
        print(f"Omega II Running Count: {self.running_count}")
        print(f"Remaining Decks: {remaining_decks:.1f}")
        print(f"True Count: {self.get_true_count()}")
        print(f"{'='*60}")
        
        # Reset player hands for this round
        for name in self.player_names:
            self.player_hands[name] = []
            self.player_results[name] = "active"
        
        # Set bet (only for main player)
        self.current_bet = self.get_bet_amount()
        true_count = self.get_true_count()
        
        print(f"\n{Colors.colorize('BETTING INFORMATION:', Colors.BOLD)}")
        print(f"Your bet: ${self.current_bet}")
        print(f"True Count: {true_count}")
        
        # Explain betting reasoning
        if true_count <= 0:
            bet_reason = "Minimum bet (unfavorable count)"
        elif true_count <= 1:
            bet_reason = "Minimum bet (low positive count)"
        elif true_count <= 2:
            bet_reason = "2 units (moderate positive count)"
        elif true_count <= 3:
            bet_reason = "4 units (good positive count)"
        elif true_count <= 4:
            bet_reason = "6 units (very good positive count)"
        elif true_count <= 5:
            bet_reason = "8 units (excellent positive count)"
        else:
            bet_reason = f"Maximum bet (extremely favorable count)"
        
        print(f"Betting Strategy: {bet_reason}")
        print(f"{'='*60}")
        
        # Deal initial cards to all players
        print(f"\n{Colors.colorize('DEALING INITIAL CARDS', Colors.BOLD)}")
        
        # First card to each player
        for name in self.player_names:
            card = self.get_card_input(f"Enter {name}'s first card: ")
            if card == 'RESTART':
                return card.lower()
            self.add_card_to_dealt(card)
            self.player_hands[name].append(card)
        
        # Second card to each player
        for name in self.player_names:
            card = self.get_card_input(f"Enter {name}'s second card: ")
            if card == 'RESTART':
                return card.lower()
            self.add_card_to_dealt(card)
            self.player_hands[name].append(card)
        
        # Dealer's upcard (after all player cards are dealt)
        dealer_upcard = self.get_card_input("Enter dealer's upcard: ")
        if dealer_upcard == 'RESTART':
            return dealer_upcard.lower()
        self.add_card_to_dealt(dealer_upcard)
        dealer_cards = [dealer_upcard]
        
        # Display all initial hands
        print(f"\n{Colors.colorize('INITIAL HANDS:', Colors.BOLD)}")
        for name in self.player_names:
            hand_value = self.calculate_hand_value(self.player_hands[name])
            print(f"{name}: {self.player_hands[name]} (Value: {hand_value})")
        print(f"Dealer upcard: {dealer_upcard}")
        
        # Check for insurance (only for main player)
        if dealer_upcard == 'A':
            insurance_choice = input(f"Dealer shows Ace. Take insurance for {self.player_names[0]}? (y/n): ").lower()
            if insurance_choice == 'y':
                print("Insurance taken (half of main bet)")
        
        # Play each player's hand
        for i, name in enumerate(self.player_names):
            print(f"\n{Colors.colorize(f'PLAYING {name.upper()}S HAND', Colors.CYAN)}")
            
            # Check for blackjack
            if self.calculate_hand_value(self.player_hands[name]) == 21:
                print(f"{name} has BLACKJACK!")
                self.player_results[name] = "blackjack"
                continue
            
            # Only provide strategy for main player (first player)
            if i == 0:
                final_hand, result = self.play_hand(self.player_hands[name], dealer_upcard, f"{name} - ")
                if result == 'restart':
                    return result
                
                # Handle splitting for main player
                if result == "split":
                    result = self.handle_split(self.player_hands[name], dealer_upcard, name)
                    if result == 'restart':
                        return result
                else:
                    self.player_hands[name] = final_hand
                    self.player_results[name] = result
            else:
                # For other players, just track their cards manually
                result = self.track_other_player_hand(name, dealer_upcard)
                if result == 'restart':
                    return result
        
        # Play dealer's hand
        print(f"\n{Colors.colorize('DEALERS TURN', Colors.BOLD)}")
        dealer_hole_card = self.get_card_input("Enter dealer's hole card: ")
        if dealer_hole_card == 'RESTART':
            return dealer_hole_card.lower()
        self.add_card_to_dealt(dealer_hole_card)
        dealer_cards.append(dealer_hole_card)
        
        dealer_cards, dealer_result = self.play_dealer_hand(dealer_cards)
        if dealer_result == 'restart':
            return dealer_result
        
        # Determine results and calculate payout (only for main player)
        print(f"\n{Colors.colorize('ROUND RESULTS:', Colors.BOLD)}")
        
        main_player = self.player_names[0]
        total_payout = 0
        
        # Check if main player split
        if f"{main_player}_hand1" in self.player_hands:
            # Handle split hands
            hand1 = self.player_hands[f"{main_player}_hand1"]
            hand2 = self.player_hands[f"{main_player}_hand2"]
            result1 = self.player_results[f"{main_player}_hand1"]
            result2 = self.player_results[f"{main_player}_hand2"]
            
            winner1 = self.determine_winner(hand1, dealer_cards, result1)
            winner2 = self.determine_winner(hand2, dealer_cards, result2)
            
            # Calculate payouts for both hands
            bet_multiplier = 2 if result1 == "double" else 1
            if winner1 == "player":
                total_payout += self.current_bet * bet_multiplier
            elif winner1 == "blackjack":
                total_payout += int(self.current_bet * 1.5 * bet_multiplier)
            elif winner1 == "dealer":
                total_payout -= self.current_bet * bet_multiplier
            
            bet_multiplier = 2 if result2 == "double" else 1
            if winner2 == "player":
                total_payout += self.current_bet * bet_multiplier
            elif winner2 == "blackjack":
                total_payout += int(self.current_bet * 1.5 * bet_multiplier)
            elif winner2 == "dealer":
                total_payout -= self.current_bet * bet_multiplier
            
            print(f"\n{Colors.colorize(f'{main_player.upper()} SPLIT HANDS RESULTS:', Colors.BOLD)}")
            print(f"Hand 1: {hand1} (Value: {self.calculate_hand_value(hand1)}) - {Colors.colorize(winner1.upper(), Colors.GREEN if winner1 in ['player', 'blackjack'] else Colors.RED if winner1 == 'dealer' else Colors.ORANGE)}")
            print(f"Hand 2: {hand2} (Value: {self.calculate_hand_value(hand2)}) - {Colors.colorize(winner2.upper(), Colors.GREEN if winner2 in ['player', 'blackjack'] else Colors.RED if winner2 == 'dealer' else Colors.ORANGE)}")
            
        elif main_player in self.player_hands:
            # Handle regular hand
            winner = self.determine_winner(self.player_hands[main_player], dealer_cards, self.player_results[main_player])
            
            # Calculate payout
            bet_multiplier = 2 if self.player_results[main_player] == "double" else 1
            
            if winner == "blackjack":
                total_payout = int(self.current_bet * 1.5)  # 3:2 payout
            elif winner == "player":
                total_payout = self.current_bet * bet_multiplier
            elif winner == "dealer":
                total_payout = -self.current_bet * bet_multiplier
            
            print(f"\n{main_player} result: {Colors.colorize(winner.upper(), Colors.GREEN if winner in ['player', 'blackjack'] else Colors.RED if winner == 'dealer' else Colors.ORANGE)}")
        
        self.player_balance += total_payout
        print(f"Payout: {Colors.colorize(f'{'+' if total_payout >= 0 else ''}${total_payout}', Colors.GREEN if total_payout >= 0 else Colors.RED)}")
        
        # Display other players' results (for tracking purposes)
        for name in self.player_names[1:]:
            if name in self.player_hands:
                winner = self.determine_winner(self.player_hands[name], dealer_cards, self.player_results[name])
                print(f"{name} result: {Colors.colorize(winner.upper(), Colors.GREEN if winner in ['player', 'blackjack'] else Colors.RED if winner == 'dealer' else Colors.ORANGE)}")
            elif f"{name}_hand1" in self.player_hands:
                # Handle split hands for other players
                hand1 = self.player_hands[f"{name}_hand1"]
                hand2 = self.player_hands[f"{name}_hand2"]
                result1 = self.player_results[f"{name}_hand1"]
                result2 = self.player_results[f"{name}_hand2"]
                
                winner1 = self.determine_winner(hand1, dealer_cards, result1)
                winner2 = self.determine_winner(hand2, dealer_cards, result2)
                
                print(f"{name} Hand 1: {Colors.colorize(winner1.upper(), Colors.GREEN if winner1 in ['player', 'blackjack'] else Colors.RED if winner1 == 'dealer' else Colors.ORANGE)}")
                print(f"{name} Hand 2: {Colors.colorize(winner2.upper(), Colors.GREEN if winner2 in ['player', 'blackjack'] else Colors.RED if winner2 == 'dealer' else Colors.ORANGE)}")
        
        # Display game information
        self.display_omega_board()
        print(f"\nWonging Status: {Colors.colorize(self.get_wonging_status(), Colors.CYAN)}")
        print(f"New Balance: {Colors.colorize(f'${self.player_balance}', Colors.BOLD)}")
        
        return "continue"
    
    def handle_split(self, original_hand, dealer_upcard, player_name):
        """Handle splitting for the main player"""
        print(f"\nSplitting {player_name}'s hand...")
        hand1_cards = [original_hand[0]]
        hand2_cards = [original_hand[1]]
        
        # Deal cards to both hands first
        card1 = self.get_card_input(f"Enter card for {player_name}'s first hand: ")
        if card1 == 'RESTART':
            return card1.lower()
        self.add_card_to_dealt(card1)
        hand1_cards.append(card1)
        
        card2 = self.get_card_input(f"Enter card for {player_name}'s second hand: ")
        if card2 == 'RESTART':
            return card2.lower()
        self.add_card_to_dealt(card2)
        hand2_cards.append(card2)
        
        # Display both hands simultaneously
        print(f"\n" + "="*50)
        print(f"{player_name.upper()}'S SPLIT HANDS:")
        print(f"Hand 1: {hand1_cards} (Value: {self.calculate_hand_value(hand1_cards)})")
        print(f"Hand 2: {hand2_cards} (Value: {self.calculate_hand_value(hand2_cards)})")
        print(f"Dealer upcard: {dealer_upcard}")
        print("="*50)
        
        # Play first hand
        print(f"\n{Colors.colorize(f'PLAYING {player_name.upper()} HAND 1', Colors.CYAN)}")
        final_hand1, result1 = self.play_hand(hand1_cards, dealer_upcard, f"{player_name} Hand 1 - ")
        if result1 == 'restart':
            return result1
        
        # Play second hand  
        print(f"\n{Colors.colorize(f'PLAYING {player_name.upper()} HAND 2', Colors.CYAN)}")
        final_hand2, result2 = self.play_hand(hand2_cards, dealer_upcard, f"{player_name} Hand 2 - ")
        if result2 == 'restart':
            return result2
        
        # Store split hands (we'll handle this differently in the main round logic)
        self.player_hands[f"{player_name}_hand1"] = final_hand1
        self.player_hands[f"{player_name}_hand2"] = final_hand2
        self.player_results[f"{player_name}_hand1"] = result1
        self.player_results[f"{player_name}_hand2"] = result2
        
        # Remove the original hand
        del self.player_hands[player_name]
        del self.player_results[player_name]
        
        return "continue"
    
    def track_other_player_hand(self, player_name, dealer_upcard):
        """Track other players' actions without providing strategy"""
        print(f"{player_name}'s turn - tracking cards only")
        current_hand = self.player_hands[player_name][:]
        
        while True:
            hand_value = self.calculate_hand_value(current_hand)
            print(f"{player_name}: {current_hand} (Value: {hand_value})")
            
            if hand_value > 21:
                print(f"{player_name} BUST!")
                self.player_results[player_name] = "bust"
                break
            
            action = input(f"What did {player_name} do? (hit-h, stand-s, double-d, split-p, bust-b): ").lower().strip()
            
            # Normalize action input
            if action in ['h', 'hit']:
                action = "hit"
            elif action in ['s', 'stand']:
                action = "stand"
            elif action in ['d', 'double']:
                action = "double"
            elif action in ['p', 'split']:
                action = "split"
            elif action in ['b', 'bust']:
                action = "bust"
            elif action == 'restart':
                return action
            
            if action == "hit":
                card = self.get_card_input(f"Enter card {player_name} received: ")
                if card == 'RESTART':
                    return card.lower()
                self.add_card_to_dealt(card)
                current_hand.append(card)
                
            elif action == "stand":
                self.player_results[player_name] = "stand"
                break
                
            elif action == "double":
                card = self.get_card_input(f"Enter card {player_name} received: ")
                if card == 'RESTART':
                    return card.lower()
                self.add_card_to_dealt(card)
                current_hand.append(card)
                self.player_results[player_name] = "double"
                break
                
            elif action == "split":
                # Handle split for other players (simplified)
                return self.track_other_player_split(player_name, dealer_upcard)
                
            elif action == "bust":
                self.player_results[player_name] = "bust"
                break
                
            else:
                print("Invalid action. Use: h/hit, s/stand, d/double, p/split, b/bust")
        
        self.player_hands[player_name] = current_hand
        return "continue"
    
    def track_other_player_split(self, player_name, dealer_upcard):
        """Track split hands for other players"""
        print(f"{player_name} is splitting...")
        original_hand = self.player_hands[player_name]
        
        # Get cards for both split hands
        card1 = self.get_card_input(f"Enter card for {player_name}'s first split hand: ")
        if card1 == 'RESTART':
            return card1.lower()
        self.add_card_to_dealt(card1)
        
        card2 = self.get_card_input(f"Enter card for {player_name}'s second split hand: ")
        if card2 == 'RESTART':
            return card2.lower()
        self.add_card_to_dealt(card2)
        
        hand1 = [original_hand[0], card1]
        hand2 = [original_hand[1], card2]
        
        print(f"{player_name}'s split hands:")
        print(f"Hand 1: {hand1} (Value: {self.calculate_hand_value(hand1)})")
        print(f"Hand 2: {hand2} (Value: {self.calculate_hand_value(hand2)})")
        
        # Track first hand
        result1 = self.track_other_player_hand_simple(f"{player_name} Hand 1", hand1)
        if result1 == 'restart':
            return result1
        
        # Track second hand
        result2 = self.track_other_player_hand_simple(f"{player_name} Hand 2", hand2)
        if result2 == 'restart':
            return result2
        
        # Store both hands
        self.player_hands[f"{player_name}_hand1"] = hand1
        self.player_hands[f"{player_name}_hand2"] = hand2
        self.player_results[f"{player_name}_hand1"] = result1
        self.player_results[f"{player_name}_hand2"] = result2
        
        # Remove original hand
        del self.player_hands[player_name]
        del self.player_results[player_name]
        
        return "continue"
    
    def track_other_player_hand_simple(self, hand_name, current_hand):
        """Simple tracking for individual split hands"""
        while True:
            hand_value = self.calculate_hand_value(current_hand)
            print(f"{hand_name}: {current_hand} (Value: {hand_value})")
            
            if hand_value > 21:
                print(f"{hand_name} BUST!")
                return "bust"
            
            action = input(f"What happened to {hand_name}? (hit/stand/double/bust): ").lower().strip()
            
            if action == 'restart':
                return action
            
            if action == "hit":
                card = self.get_card_input(f"Enter card for {hand_name}: ")
                if card == 'RESTART':
                    return card.lower()
                self.add_card_to_dealt(card)
                current_hand.append(card)
                
            elif action == "stand":
                return "stand"
                
            elif action == "double":
                card = self.get_card_input(f"Enter card for {hand_name}: ")
                if card == 'RESTART':
                    return card.lower()
                self.add_card_to_dealt(card)
                current_hand.append(card)
                return "double"
                
            elif action == "bust":
                return "bust"
                
            else:
                print("Invalid action. Use: hit, stand, double, or bust")
    
    def run(self):
        """Main game loop"""
        print(f"{Colors.colorize('Welcome to Blackjack with Omega II Card Counting!', Colors.BOLD + Colors.CYAN)}")
        print(f"Players: {', '.join(self.player_names)}")
        print("Commands: 'restart' to reset, 'undo' for last card, 'undo+' for multiple moves, 'quit' to exit")
        
        while True:
            if self.player_balance <= 0:
                print("Game Over - Out of money!")
                break
            
            result = self.play_round()
            
            if result == "restart":
                print("\nRestarting game...")
                self.reset_game()
                continue
            
            # Check if player wants to continue
            continue_choice = input("\nPlay another round? (y/n/restart): ").lower()
            if continue_choice == 'n':
                break
            elif continue_choice == 'restart':
                print("\nRestarting game...")
                self.reset_game()

        print(f"\nFinal balance: ${self.player_balance}")
        print("Thanks for playing!")

# Run the game
if __name__ == "__main__":
    game = BlackjackGame()
    game.run()

