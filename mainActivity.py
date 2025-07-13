import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from main import BlackjackGame, Colors
import sys
from io import StringIO

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack with Omega II Card Counting")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)  # Minimum size to ensure all components are visible
        self.root.configure(bg='#0a3d0a')  # Darker casino green background
        
        # Modern color scheme
        self.colors = {
            'bg_primary': '#0a3d0a',      # Dark casino green
            'bg_secondary': '#1a5d1a',    # Medium green
            'bg_tertiary': '#2d7d2d',     # Light green
            'panel_bg': '#1e4a1e',        # Panel background
            'card_bg': '#234d23',         # Card background
            'text_primary': '#ffffff',    # White text
            'text_secondary': '#e0e0e0',  # Light gray text
            'text_accent': '#ffd700',     # Gold text
            'button_primary': '#2e7d32',  # Green button
            'button_secondary': '#455a64', # Gray button
            'button_danger': '#d32f2f',   # Red button
            'button_warning': '#f57c00',  # Orange button
            'button_success': '#388e3c',  # Success green
            'button_info': '#1976d2',     # Blue button
            'accent_gold': '#ffd700',     # Gold accent
            'accent_cyan': '#00bcd4'      # Cyan accent
        }
        
        # Make window resizable and responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Initialize game
        self.game = None
        self.game_thread = None
        self.is_game_running = False
        
        # Create main interface
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main container with proper grid management
        main_container = tk.Frame(self.root, bg='#0d5d0d')
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        
        # Title
        title_frame = tk.Frame(main_container, bg='#0d5d0d')
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        
        title_label = tk.Label(title_frame, 
                              text="BLACKJACK with Omega II Card Counting", 
                              font=("Arial", 24, "bold"),
                              fg='gold', bg='#0d5d0d')
        title_label.pack()
        
        # Left panel - Game controls and info (fixed width, expandable height)
        left_panel = tk.Frame(main_container, bg='#1a4d1a', relief=tk.RAISED, bd=2, width=350)
        left_panel.grid(row=1, column=0, sticky="ns", padx=(0, 10))
        left_panel.grid_propagate(False)  # Maintain fixed width
        
        # Create scrollable frame for left panel
        left_canvas = tk.Canvas(left_panel, bg='#1a4d1a', highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=left_canvas.yview)
        left_scrollable = tk.Frame(left_canvas, bg='#1a4d1a')
        
        left_scrollable.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        
        left_canvas.create_window((0, 0), window=left_scrollable, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        left_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        left_scrollbar.pack(side="right", fill="y")
        
        # Game setup section
        setup_frame = tk.LabelFrame(left_scrollable, text="Game Setup", 
                                   bg='#1a4d1a', fg='white', font=("Arial", 12, "bold"))
        setup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(setup_frame, text="Number of Decks:", 
                bg='#1a4d1a', fg='white').pack(anchor=tk.W, padx=5, pady=2)
        self.decks_var = tk.StringVar(value="6")
        decks_entry = tk.Entry(setup_frame, textvariable=self.decks_var, width=10)
        decks_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        tk.Label(setup_frame, text="Number of Players:", 
                bg='#1a4d1a', fg='white').pack(anchor=tk.W, padx=5, pady=2)
        self.players_var = tk.StringVar(value="1")
        players_entry = tk.Entry(setup_frame, textvariable=self.players_var, width=10)
        players_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        self.start_button = tk.Button(setup_frame, text="Start New Game", 
                                     command=self.start_new_game,
                                     bg='#4CAF50', fg='white', font=("Arial", 10, "bold"))
        self.start_button.pack(pady=10)
        
        # Count information section
        count_frame = tk.LabelFrame(left_scrollable, text="Omega II Count Info", 
                                   bg='#1a4d1a', fg='white', font=("Arial", 12, "bold"))
        count_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.running_count_label = tk.Label(count_frame, text="Running Count: 0", 
                                           bg='#1a4d1a', fg='yellow', font=("Arial", 11, "bold"))
        self.running_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.true_count_label = tk.Label(count_frame, text="True Count: 0", 
                                        bg='#1a4d1a', fg='yellow', font=("Arial", 11, "bold"))
        self.true_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.remaining_decks_label = tk.Label(count_frame, text="Remaining Decks: 6.0", 
                                             bg='#1a4d1a', fg='yellow', font=("Arial", 11, "bold"))
        self.remaining_decks_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.penetration_label = tk.Label(count_frame, text="Deck Penetration: 0%", 
                                         bg='#1a4d1a', fg='yellow', font=("Arial", 11, "bold"))
        self.penetration_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Betting information
        betting_frame = tk.LabelFrame(left_scrollable, text="Betting Info", 
                                     bg='#1a4d1a', fg='white', font=("Arial", 12, "bold"))
        betting_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.balance_label = tk.Label(betting_frame, text="Balance: $1000", 
                                     bg='#1a4d1a', fg='lightgreen', font=("Arial", 11, "bold"))
        self.balance_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.bet_label = tk.Label(betting_frame, text="Current Bet: $1", 
                                 bg='#1a4d1a', fg='lightgreen', font=("Arial", 11, "bold"))
        self.bet_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.wonging_label = tk.Label(betting_frame, text="Wonging: NEUTRAL", 
                                     bg='#1a4d1a', fg='cyan', font=("Arial", 11, "bold"))
        self.wonging_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Strategy recommendation
        strategy_frame = tk.LabelFrame(left_scrollable, text="Strategy Recommendation", 
                                      bg='#1a4d1a', fg='white', font=("Arial", 12, "bold"))
        strategy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.strategy_label = tk.Label(strategy_frame, text="No recommendation", 
                                      bg='#1a4d1a', fg='white', font=("Arial", 14, "bold"))
        self.strategy_label.pack(padx=5, pady=10)
        
        # Right panel - Game area (expandable)
        right_panel = tk.Frame(main_container, bg='#0d5d0d')
        right_panel.grid(row=1, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Game display area with scrolling
        game_frame = tk.LabelFrame(right_panel, text="Game Table", 
                                  bg='#0d5d0d', fg='white', font=("Arial", 12, "bold"))
        game_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        game_frame.grid_rowconfigure(1, weight=1)
        game_frame.grid_columnconfigure(0, weight=1)
        
        # Dealer area
        dealer_frame = tk.Frame(game_frame, bg='#0d5d0d')
        dealer_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        tk.Label(dealer_frame, text="DEALER", 
                bg='#0d5d0d', fg='white', font=("Arial", 14, "bold")).pack()
        
        self.dealer_cards_label = tk.Label(dealer_frame, text="Cards: []", 
                                          bg='#0d5d0d', fg='white', font=("Arial", 12))
        self.dealer_cards_label.pack()
        
        # Player areas with scrolling
        players_canvas = tk.Canvas(game_frame, bg='#0d5d0d', highlightthickness=0)
        players_scrollbar = ttk.Scrollbar(game_frame, orient="vertical", command=players_canvas.yview)
        self.players_frame = tk.Frame(players_canvas, bg='#0d5d0d')
        
        self.players_frame.bind(
            "<Configure>",
            lambda e: players_canvas.configure(scrollregion=players_canvas.bbox("all"))
        )
        
        players_canvas.create_window((0, 0), window=self.players_frame, anchor="nw")
        players_canvas.configure(yscrollcommand=players_scrollbar.set)
        
        players_canvas.grid(row=1, column=0, sticky="nsew")
        players_scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.player_labels = {}
        
        # Card input section (fixed at bottom)
        input_frame = tk.Frame(right_panel, bg='#1a4d1a', relief=tk.RAISED, bd=2)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        input_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(input_frame, text="Card Input", 
                bg='#1a4d1a', fg='white', font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
        # Card input row
        self.card_prompt_label = tk.Label(input_frame, text="Enter card:", 
                                         bg='#1a4d1a', fg='white', font=("Arial", 10))
        self.card_prompt_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.card_entry = tk.Entry(input_frame, font=("Arial", 12), width=15)
        self.card_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.card_entry.bind('<Return>', self.submit_card)
        # Real-time updates will be handled by submit_card method
        
        self.submit_button = tk.Button(input_frame, text="Submit", 
                                      command=self.submit_card,
                                      bg='#4CAF50', fg='white')
        self.submit_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Action buttons row
        action_frame = tk.Frame(input_frame, bg='#1a4d1a')
        action_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        self.hit_button = tk.Button(action_frame, text="Hit (H)", 
                                   command=lambda: self.submit_action("hit"),
                                   bg='#f44336', fg='white', state=tk.DISABLED)
        self.hit_button.pack(side=tk.LEFT, padx=2)
        
        self.stand_button = tk.Button(action_frame, text="Stand (S)", 
                                     command=lambda: self.submit_action("stand"),
                                     bg='#ff9800', fg='white', state=tk.DISABLED)
        self.stand_button.pack(side=tk.LEFT, padx=2)
        
        self.double_button = tk.Button(action_frame, text="Double (D)", 
                                      command=lambda: self.submit_action("double"),
                                      bg='#4CAF50', fg='white', state=tk.DISABLED)
        self.double_button.pack(side=tk.LEFT, padx=2)
        
        self.split_button = tk.Button(action_frame, text="Split (P)", 
                                     command=lambda: self.submit_action("split"),
                                     bg='#9c27b0', fg='white', state=tk.DISABLED)
        self.split_button.pack(side=tk.LEFT, padx=2)
        
        self.bust_button = tk.Button(action_frame, text="Bust (B)", 
                                    command=lambda: self.submit_action("bust"),
                                    bg='#d32f2f', fg='white', state=tk.DISABLED)
        self.bust_button.pack(side=tk.LEFT, padx=2)
        
        # Utility buttons row
        util_frame = tk.Frame(input_frame, bg='#1a4d1a')
        util_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        self.undo_button = tk.Button(util_frame, text="Undo", 
                                    command=self.undo_last,
                                    bg='#607d8b', fg='white')
        self.undo_button.pack(side=tk.LEFT, padx=2)
        
        self.restart_button = tk.Button(util_frame, text="Restart Round", 
                                       command=self.restart_round,
                                       bg='#795548', fg='white')
        self.restart_button.pack(side=tk.LEFT, padx=2)
        
        help_button = tk.Button(util_frame, text="Help (F1)", 
                                command=self.show_help,
                                bg='#2196F3', fg='white')
        help_button.pack(side=tk.LEFT, padx=2)
        
        # Bind F1 for help
        self.root.bind('<F1>', lambda e: self.show_help())
        
        # Status bar (fixed at bottom)
        self.status_label = tk.Label(self.root, text="Ready to start game", 
                                    bg='#333333', fg='white', font=("Arial", 10))
        self.status_label.grid(row=1, column=0, sticky="ew")
        
        # Variables for game state
        self.waiting_for_input = False
        self.input_type = None
        self.current_input = None
        self.input_event = threading.Event()
        
        # Keyboard shortcuts
        self.root.bind('<h>', lambda e: self.submit_action("hit") if self.input_type in ["action", "other_action"] else None)
        self.root.bind('<s>', lambda e: self.submit_action("stand") if self.input_type in ["action", "other_action"] else None)
        self.root.bind('<d>', lambda e: self.submit_action("double") if self.input_type in ["action", "other_action"] else None)
        self.root.bind('<p>', lambda e: self.submit_action("split") if self.input_type in ["action", "other_action"] else None)
        self.root.bind('<b>', lambda e: self.submit_action("bust") if self.input_type == "other_action" else None)
        self.root.bind('<Control-z>', lambda e: self.undo_last())
        self.root.bind('<Control-r>', lambda e: self.restart_round())
        
        # Focus management
        self.root.focus_set()
        
    def start_new_game(self):
        """Start a new game with the specified parameters"""
        try:
            num_decks = int(self.decks_var.get())
            num_players = int(self.players_var.get())
            
            if num_decks < 1 or num_decks > 8:
                messagebox.showerror("Error", "Number of decks must be between 1 and 8")
                return
                
            if num_players < 1 or num_players > 6:
                messagebox.showerror("Error", "Number of players must be between 1 and 6")
                return
                
            # Create game instance
            self.game = BlackjackGameGUI(num_decks, num_players, self)
            
            # Create player display areas
            self.create_player_areas(num_players)
            
            # Update displays
            self.update_displays()
            
            # Disable start button
            self.start_button.config(state=tk.DISABLED)
            
            # Start game in separate thread
            self.is_game_running = True
            self.game_thread = threading.Thread(target=self.run_game_loop, daemon=True)
            self.game_thread.start()
            
            self.update_status("Game started! Round 1 beginning...")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for decks and players")
    
    def create_player_areas(self, num_players):
        """Create display areas for all players"""
        # Clear existing player displays
        for widget in self.players_frame.winfo_children():
            widget.destroy()
        self.player_labels.clear()
        
        # Create new player displays
        for i in range(num_players):
            player_name = f"Player {i + 1}"
            player_frame = tk.Frame(self.players_frame, bg='#1a4d1a', relief=tk.RAISED, bd=1)
            player_frame.pack(fill=tk.X, pady=5, padx=10)
            player_frame.grid_columnconfigure(1, weight=1)
            
            # Player name and info
            info_frame = tk.Frame(player_frame, bg='#1a4d1a')
            info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
            
            name_label = tk.Label(info_frame, text=player_name, 
                                 bg='#1a4d1a', fg='white', font=("Arial", 12, "bold"))
            name_label.pack(side=tk.LEFT)
            
            if i == 0:  # Main player
                status_label = tk.Label(info_frame, text="(You)", 
                                       bg='#1a4d1a', fg='yellow', font=("Arial", 10))
                status_label.pack(side=tk.LEFT, padx=5)
            
            # Cards display
            cards_label = tk.Label(player_frame, text="Cards: []", 
                                  bg='#1a4d1a', fg='white', font=("Arial", 11),
                                  wraplength=500, justify=tk.LEFT)
            cards_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
            
            # Value display
            value_label = tk.Label(player_frame, text="Value: 0", 
                                  bg='#1a4d1a', fg='lightblue', font=("Arial", 11))
            value_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
            
            # Result display
            result_label = tk.Label(player_frame, text="", 
                                   bg='#1a4d1a', fg='white', font=("Arial", 11, "bold"))
            result_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
            
            self.player_labels[player_name] = {
                'cards': cards_label,
                'value': value_label,
                'result': result_label
            }
    
    def update_displays(self):
        """Update all display elements"""
        if not self.game:
            return
            
        # Update count information
        self.running_count_label.config(text=f"Running Count: {self.game.running_count}")
        self.true_count_label.config(text=f"True Count: {self.game.get_true_count()}")
        
        remaining_decks = sum(self.game.deck.values()) / 52
        self.remaining_decks_label.config(text=f"Remaining Decks: {remaining_decks:.1f}")
        
        penetration = self.game.get_deck_penetration()
        self.penetration_label.config(text=f"Deck Penetration: {penetration:.1f}%")
        
        # Update betting information
        self.balance_label.config(text=f"Balance: ${self.game.player_balance}")
        self.bet_label.config(text=f"Current Bet: ${self.game.current_bet}")
        
        wonging_status = self.game.get_wonging_status()
        self.wonging_label.config(text=f"Wonging: {wonging_status}")
        
        # Update player hands
        for player_name, labels in self.player_labels.items():
            if player_name in self.game.player_hands:
                cards = self.game.player_hands[player_name]
                value = self.game.calculate_hand_value(cards)
                labels['cards'].config(text=f"Cards: {cards}")
                labels['value'].config(text=f"Value: {value}")
                
                # Update result
                if player_name in self.game.player_results:
                    result = self.game.player_results[player_name]
                    if result != "active":
                        labels['result'].config(text=f"Result: {result.upper()}")
                    else:
                        labels['result'].config(text="")
            else:
                # Check for split hands
                if f"{player_name}_hand1" in self.game.player_hands:
                    hand1 = self.game.player_hands[f"{player_name}_hand1"]
                    hand2 = self.game.player_hands[f"{player_name}_hand2"]
                    value1 = self.game.calculate_hand_value(hand1)
                    value2 = self.game.calculate_hand_value(hand2)
                    labels['cards'].config(text=f"Hand1: {hand1} | Hand2: {hand2}")
                    labels['value'].config(text=f"Values: {value1} | {value2}")
        
        # Update dealer cards
        if hasattr(self.game, 'dealer_cards') and self.game.dealer_cards:
            dealer_value = self.game.calculate_hand_value(self.game.dealer_cards)
            self.dealer_cards_label.config(text=f"Cards: {self.game.dealer_cards} (Value: {dealer_value})")
    
    def update_strategy_display(self, action, color_name):
        """Update the strategy recommendation display"""
        color_map = {
            'RED': '#f44336',
            'ORANGE': '#ff9800', 
            'GREEN': '#4CAF50',
            'PURPLE': '#9c27b0'
        }
        color = color_map.get(color_name, 'white')
        self.strategy_label.config(text=action, fg=color)
    
    def wait_for_input(self, prompt, input_type="card"):
        """Wait for user input (card or action)"""
        self.waiting_for_input = True
        self.input_type = input_type
        self.current_input = None
        
        self.update_status(prompt)
        self.card_prompt_label.config(text=prompt)
        
        if input_type == "card":
            self.enable_card_input()
            self.disable_action_buttons()
        elif input_type == "action":
            self.disable_card_input()
            self.enable_action_buttons()
        elif input_type == "other_action":
            self.enable_card_input()
            self.enable_action_buttons()  # Enable action buttons for other player actions too
        
        # Wait for input
        self.input_event.clear()
        self.input_event.wait()
        
        self.waiting_for_input = False
        return self.current_input
    
    def submit_card(self, event=None):
        """Submit card input with real-time validation and updates"""
        if not self.waiting_for_input:
            return
            
        input_text = self.card_entry.get().strip().upper()
        if input_text:
            # Handle action input for other players
            if self.input_type == "other_action":
                action_map = {'H': 'hit', 'S': 'stand', 'D': 'double', 'P': 'split', 'B': 'bust',
                             'HIT': 'hit', 'STAND': 'stand', 'DOUBLE': 'double', 'SPLIT': 'split', 'BUST': 'bust'}
                if input_text in action_map:
                    self.current_input = action_map[input_text]
                    self.card_entry.delete(0, tk.END)
                    self.input_event.set()
                    return
                else:
                    self.update_status("Invalid action. Use: h/hit, s/stand, d/double, p/split, b/bust")
                    self.card_entry.select_range(0, tk.END)
                    return
            
            # Handle card input
            card = input_text
            # Normalize card input for validation
            normalized_card = card
            if card == '1':
                normalized_card = 'A'
            elif card in ['J', 'Q', 'K']:
                normalized_card = card.upper()
            
            # Validate card before submitting
            valid_cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            if normalized_card in valid_cards:
                if self.game and normalized_card in self.game.deck and self.game.deck[normalized_card] > 0:
                    self.current_input = normalized_card
                    self.card_entry.delete(0, tk.END)
                    # Update displays immediately after card submission
                    self.root.after(100, self.update_displays)
                    self.input_event.set()
                else:
                    # Show error for cards not in deck
                    self.update_status(f"No more {normalized_card}s in deck!")
                    self.card_entry.select_range(0, tk.END)
            else:
                # Show error for invalid cards
                self.update_status("Invalid card. Enter: A/1, 2-10, J, Q, K")
                self.card_entry.select_range(0, tk.END)
    
    def submit_action(self, action):
        """Submit action input"""
        if not self.waiting_for_input:
            return
            
        if self.input_type == "action" or self.input_type == "other_action":
            self.current_input = action
            self.input_event.set()
    
    def enable_card_input(self):
        """Enable card input controls"""
        self.card_entry.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)
        self.card_entry.focus()
    
    def disable_card_input(self):
        """Disable card input controls"""
        self.card_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
    
    def enable_action_buttons(self):
        """Enable action buttons"""
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        self.double_button.config(state=tk.NORMAL)
        self.split_button.config(state=tk.NORMAL)
        self.bust_button.config(state=tk.NORMAL)
    
    def disable_action_buttons(self):
        """Disable action buttons"""
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.double_button.config(state=tk.DISABLED)
        self.split_button.config(state=tk.DISABLED)
        self.bust_button.config(state=tk.DISABLED)
    
    def undo_last(self):
        """Undo last action"""
        if self.game and hasattr(self.game, 'undo_last_action'):
            self.game.undo_last_action()
            self.update_displays()
    
    def restart_round(self):
        """Restart current round"""
        if self.waiting_for_input:
            self.current_input = "restart"
            self.input_event.set()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def run_game_loop(self):
        """Main game loop running in separate thread"""
        try:
            while self.is_game_running and self.game:
                result = self.game.play_round()
                
                if result == "restart":
                    self.root.after(0, self.update_status, "Round restarted")
                    continue
                
                # Update displays after round
                self.root.after(0, self.update_displays)
                
                # Ask if player wants to continue
                self.root.after(0, self.show_continue_dialog)
                
                # Wait for continue decision
                self.input_event.clear()
                self.input_event.wait()
                
                if not self.current_input:
                    break
                    
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Game Error", str(e)))
        finally:
            self.is_game_running = False
            self.root.after(0, self.enable_new_game)
    
    def show_continue_dialog(self):
        """Show dialog asking if player wants to continue"""
        result = messagebox.askyesno("Continue?", "Play another round?")
        self.current_input = result
        self.input_event.set()
    
    def enable_new_game(self):
        """Re-enable the start new game button"""
        self.start_button.config(state=tk.NORMAL)
        self.disable_card_input()
        self.disable_action_buttons()
        self.update_status("Game ended. Ready to start new game.")
        # Reset strategy display
        self.strategy_label.config(text="No recommendation", fg='white')
    
    def show_help(self):
        """Show help dialog with keyboard shortcuts and usage instructions"""
        help_text = """
BLACKJACK GUI - HELP

KEYBOARD SHORTCUTS:
• H - Hit (when choosing action)
• S - Stand (when choosing action)  
• D - Double (when choosing action)
• P - Split (when choosing action)
• B - Bust (for other players only)
• Enter - Submit card input
• Ctrl+Z - Undo last card
• Ctrl+R - Restart round
• F1 - Show this help

CARD INPUT:
• Enter cards as: A, 2-10, J, Q, K
• Use '1' as alternative for Ace
• Case insensitive
• Press Enter to submit

OTHER PLAYER ACTIONS:
• Type h/hit, s/stand, d/double, p/split, b/bust
• Or click the action buttons
• Or use keyboard shortcuts

GAME FLOW:
1. Set number of decks and players
2. Click "Start New Game"
3. Enter cards as prompted
4. Follow strategy recommendations
5. Use action buttons or keyboard shortcuts

STRATEGY COLORS:
• Red = Hit
• Orange = Stand
• Green = Double
• Purple = Split

The Omega II count system automatically tracks all cards
and provides optimal betting recommendations.
        """
        
        messagebox.showinfo("Blackjack GUI Help", help_text)
        

class BlackjackGameGUI(BlackjackGame):
    """Modified BlackjackGame class for GUI integration"""
    
    def __init__(self, total_decks, num_players, gui):
        self.total_decks = total_decks
        self.num_players = num_players
        self.gui = gui
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
        
        # For dealer cards tracking
        self.dealer_cards = []
    
    def get_card_input(self, prompt):
        """Get card input through GUI with real-time updates"""
        while True:
            card = self.gui.wait_for_input(prompt, "card")
            
            if card == 'RESTART':
                return card
            elif card == 'UNDO':
                if self.undo_last_action():
                    self.gui.root.after(0, self.gui.update_displays)
                    continue
                else:
                    continue
            elif card == 'UNDO+':
                self.undo_multiple_moves()
                self.gui.root.after(0, self.gui.update_displays)
                continue
            
            # Normalize card input
            if card == '1':
                card = 'A'
            elif card in ['J', 'Q', 'K']:
                card = card.upper()
            
            valid_cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            if card in valid_cards:
                if self.deck[card] > 0:
                    # Update displays immediately after successful card input
                    self.gui.root.after(0, self.gui.update_displays)
                    return card
                else:
                    self.gui.root.after(0, lambda c=card: messagebox.showwarning("Invalid Card", f"No more {c}s in deck!"))
            else:
                self.gui.root.after(0, lambda: messagebox.showwarning("Invalid Card", "Enter: A/1, 2-10, J, Q, K"))
    
    def play_hand(self, player_cards, dealer_upcard, hand_name=""):
        """Play a single hand with GUI integration"""
        # Update displays
        self.gui.root.after(0, self.gui.update_displays)
        
        # Check for blackjack
        if len(player_cards) == 2 and self.calculate_hand_value(player_cards) == 21:
            self.gui.root.after(0, self.gui.update_status, f"{hand_name}BLACKJACK!")
            return player_cards, "blackjack"
        
        can_double = len(player_cards) == 2
        can_split = len(player_cards) == 2 and player_cards[0] == player_cards[1]
        
        while True:
            player_total = self.calculate_hand_value(player_cards)
            
            if player_total > 21:
                self.gui.root.after(0, self.gui.update_status, f"{hand_name}BUST!")
                return player_cards, "bust"
            
            # Get strategy recommendation
            action, color = self.get_basic_strategy(player_cards, dealer_upcard, can_double, can_split)
            
            # Update strategy display
            color_name = {
                Colors.RED: 'RED',
                Colors.ORANGE: 'ORANGE', 
                Colors.GREEN: 'GREEN',
                Colors.PURPLE: 'PURPLE'
            }.get(color, 'WHITE')
            
            self.gui.root.after(0, self.gui.update_strategy_display, action, color_name)
            self.gui.root.after(0, self.gui.update_displays)
            
            # Get player action
            choice = self.gui.wait_for_input(f"{hand_name}Choose action (hit-h, stand-s, double-d, split-p):", "action")
            
            if choice == 'restart':
                return player_cards, choice
            
            if choice == "hit":
                card = self.get_card_input(f"{hand_name}Enter card received: ")
                if card == 'RESTART':
                    return player_cards, card.lower()
                
                if self.add_card_to_dealt(card):
                    player_cards.append(card)
                    can_double = False
                    can_split = False
                    self.gui.root.after(0, self.gui.update_displays)
                
            elif choice == "stand":
                return player_cards, "stand"
                
            elif choice == "double" and can_double:
                card = self.get_card_input(f"{hand_name}Enter card received: ")
                if card == 'RESTART':
                    return player_cards, card.lower()
                
                if self.add_card_to_dealt(card):
                    player_cards.append(card)
                    self.gui.root.after(0, self.gui.update_displays)
                    return player_cards, "double"
                
            elif choice == "split" and can_split:
                return player_cards, "split"
                
            else:
                self.gui.root.after(0, lambda: messagebox.showwarning("Invalid Action", "Invalid choice"))
    
    def track_other_player_hand(self, player_name, dealer_upcard):
        """Track other players' actions through GUI"""
        current_hand = self.player_hands[player_name][:]
        
        while True:
            hand_value = self.calculate_hand_value(current_hand)
            self.gui.root.after(0, self.gui.update_displays)
            
            if hand_value > 21:
                self.gui.root.after(0, self.gui.update_status, f"{player_name} BUST!")
                self.player_results[player_name] = "bust"
                break
            
            # Use "other_action" input type which allows text input for other players
            action = self.gui.wait_for_input(f"What did {player_name} do? (h/s/d/p/b) or click action buttons:", "other_action")
            
            # Normalize action input
            if action.lower() in ['h', 'hit']:
                action = "hit"
            elif action.lower() in ['s', 'stand']:
                action = "stand"
            elif action.lower() in ['d', 'double']:
                action = "double"
            elif action.lower() in ['p', 'split']:
                action = "split"
            elif action.lower() in ['b', 'bust']:
                action = "bust"
            elif action == 'restart':
                return action
            else:
                self.gui.root.after(0, lambda: messagebox.showwarning("Invalid Action", "Use: h/hit, s/stand, d/double, p/split, b/bust"))
                continue
            
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
                return self.track_other_player_split(player_name, dealer_upcard)
                
            elif action == "bust":
                self.player_results[player_name] = "bust"
                break
        
        self.player_hands[player_name] = current_hand
        return "continue"
    
    def play_dealer_hand(self, dealer_cards):
        """Play dealer's hand with GUI updates"""
        self.dealer_cards = dealer_cards
        self.gui.root.after(0, self.gui.update_displays)
        self.gui.root.after(0, self.gui.update_status, "Dealer's turn")
        
        while True:
            dealer_total = self.calculate_hand_value(dealer_cards)
            
            if dealer_total > 21:
                self.gui.root.after(0, self.gui.update_status, "Dealer BUST!")
                break
            
            # Dealer hits on soft 17
            if dealer_total < 17 or (dealer_total == 17 and self.is_soft_hand(dealer_cards)):
                card = self.get_card_input("Enter dealer's next card: ")
                if card == 'RESTART':
                    return dealer_cards, card.lower()
                
                if self.add_card_to_dealt(card):
                    dealer_cards.append(card)
                    self.dealer_cards = dealer_cards
                    self.gui.root.after(0, self.gui.update_displays)
            else:
                self.gui.root.after(0, self.gui.update_status, "Dealer stands")
                break
        
        return dealer_cards, "complete"
    
    def add_card_to_dealt(self, card):
        """Add a card to the dealt cards and update running count with immediate GUI updates"""
        result = super().add_card_to_dealt(card)
        if result:
            # Immediately update the GUI displays
            self.gui.root.after(0, self.gui.update_displays)
        return result


def main():
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
