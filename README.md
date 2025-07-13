# BlackJack with Omega II Card Counting

A comprehensive BlackJack game implementation with advanced card counting system, featuring both console and GUI interfaces.

## Features

### 🎯 Core Game Features
- **Multi-player support** (1-6 players)
- **Configurable deck count** (1-8 decks)
- **Complete BlackJack rules** including splits, doubles, insurance
- **Realistic game flow** with proper dealing sequence
- **Interactive gameplay** with multiple input methods

### 🧮 Advanced Card Counting
- **Omega II counting system** implementation
- **True count calculation** based on remaining decks
- **Deck penetration tracking**
- **Betting strategy recommendations**
- **Wonging recommendations** (entering/leaving based on count)

### 💻 Dual Interface Options
- **Console Interface** (`main.py`) - Text-based gameplay
- **GUI Interface** (`mainActivity.py`) - Modern tkinter-based interface

### 🎮 GUI Features
- **Modern casino-style design** with green felt theme
- **Real-time card counting display**
- **Strategy recommendations** with color-coded hints
- **Multiple input methods**: buttons, keyboard shortcuts, text input
- **Live game statistics** and betting information
- **Responsive layout** with scrollable game area

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd BlackJack
```

2. Install dependencies (if any):
```bash
pip install -r requirements.txt  # If requirements.txt exists
```

3. Run the game:
```bash
# Console version
python main.py

# GUI version
python mainActivity.py
```

## How to Play

### Starting a Game
1. **Console**: Run `python main.py` and follow prompts
2. **GUI**: Run `python mainActivity.py`, set parameters, and click "Start New Game"

### Game Controls

#### Console Interface
- Enter cards as prompted (A, 2-10, J, Q, K)
- Choose actions by typing: h (hit), s (stand), d (double), p (split)
- Use special commands: UNDO, RESTART

#### GUI Interface
- **Card Input**: Type cards in the input field or use dropdown
- **Player Actions**: Click buttons or use keyboard shortcuts
  - `H` - Hit
  - `S` - Stand  
  - `D` - Double
  - `P` - Split
  - `B` - Bust (for other players)
- **Utility Commands**:
  - `Ctrl+Z` - Undo last action
  - `Ctrl+R` - Restart round
  - `F1` - Show help

### Card Counting System

The game implements the **Omega II** counting system:
- **Low cards** (2,3,7): +1
- **Medium cards** (4,5,6): +2  
- **Neutral cards** (8,A): 0
- **High cards** (9): -1
- **Face cards** (10,J,Q,K): -2

The system provides:
- **Running Count**: Raw count of cards seen
- **True Count**: Running count divided by remaining decks
- **Betting Strategy**: Recommended bet sizes based on true count
- **Wonging Strategy**: When to enter/leave the table

## Game Rules

### Standard BlackJack Rules
- Goal: Get as close to 21 as possible without going over
- Face cards worth 10, Aces worth 1 or 11
- Dealer hits on soft 17
- BlackJack pays 3:2
- Insurance available when dealer shows Ace

### Special Actions
- **Hit**: Take another card
- **Stand**: Keep current hand
- **Double**: Double bet and take exactly one more card
- **Split**: Split pairs into two separate hands
- **Insurance**: Side bet when dealer shows Ace

## Project Structure

```
BlackJack/
├── main.py                    # Console interface and core game logic
├── mainActivity.py           # GUI interface implementation
├── test_*.py                 # Test files for various components
├── README.md                 # This file
└── .gitignore               # Git ignore patterns
```

## Testing

The project includes comprehensive test files:
- `test_gui.py` - GUI functionality tests
- `test_dealing_sequence.py` - Card dealing order validation
- `test_undo.py` - Undo system tests
- `test_fixes.py` - Bug fix validations

Run tests:
```bash
python test_gui.py
python test_dealing_sequence.py
# ... other test files
```

## Development

### Key Classes
- **BlackjackGame**: Core game logic and card counting
- **BlackjackGUI**: Main GUI application class
- **BlackjackGameGUI**: Game logic adapted for GUI interface

### Recent Improvements
- ✅ Fixed Player 2+ input handling in GUI
- ✅ Corrected dealer card timing sequence
- ✅ Added multiple input methods for better UX
- ✅ Enhanced error handling and validation
- ✅ Improved visual feedback and status updates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Omega II counting system developed by Bryce Carlson
- BlackJack rules and strategy based on standard casino play
- GUI design inspired by modern casino interfaces

---

**Note**: This is for educational purposes only. Please gamble responsibly and be aware of local laws regarding gambling applications.
