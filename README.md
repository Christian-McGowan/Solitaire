# Solitaire (Klondike) Game

A graphical implementation of the classic Klondike Solitaire card game, built with Python and Pygame. Shuffle and deal a standard deck of cards, then use drag-and-drop mechanics and automatic hints to move cards between tableau piles, foundation piles, and the waste pile until you clear all suits.

---

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Game](#running-the-game)
6. [Controls & Gameplay](#controls--gameplay)
7. [Code Structure](#code-structure)
8. [Customization](#customization)
9. [License](#license)

---

## Features

* **Difficulty Levels**: Easy (draw 1), Medium (draw 3), and Hard (draw 5).
* **Automatic Moves**: Single-click on a pile to auto-move cards to valid foundations or tableau positions.
* **Undo**: Revert the last draw or move action.
* **Drag-and-Drop**: Click and drag face-up cards (and any cards stacked beneath) to new piles.
* **Multiple Themes**: Randomly select from 10 visual themes (e.g., Basic, Casino, Pirate, Future).
* **Win Detection**: Display a "You Win!" overlay with a "Play Again" button when all cards reach the foundations.
* **Timer**: Track elapsed time in minutes and seconds.

## Prerequisites

* **Python 3.7+**
* **Pygame** (version 2.0 or newer)

## Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/your-username/solitaire-pygame.git
   cd solitaire-pygame
   ```

2. **Install dependencies**

   ```bash
   pip install pygame
   ```

## Configuration

At the top of `solitaire.py`, you can tweak settings:

```python
# Window dimensions
WIDTH, HEIGHT = 1024, 768

# Frame rate
FPS = 60

# Card dimensions
CARD_W, CARD_H = 100, 145

# Tableau vertical position
TABLEAU_Y = 250

# Vertical spacing
SPACING_DOWN = 10    # between face-down cards
SPACING_UP   = 30    # between face-up cards

# Difficulty draw counts & waste display counts
DIFFICULTY_SETTINGS = {'easy': 1, 'medium': 3, 'hard': 5}
WASTE_DISPLAY       = {'easy': 1, 'medium': 2, 'hard': 3}

# Theme colors
THEMES and THEME_CONFIG dictionaries
```

Feel free to adjust these constants to change the look and feel.

## Running the Game

Execute the main script:

```bash
python solitaire.py
```

1. On launch, select a difficulty by clicking one of the buttons!
2. The game will deal cards and begin the timer.

## Controls & Gameplay

* **Click Stock Pile** (top-left): Draw new cards into the waste pile until the deck is empty, then recycle.
* **Click Waste Card** (next to stock) to auto-move it if a valid foundation or tableau move exists.
* **Drag-and-Drop**: Click and drag the top face-up card (or a stack of cards) from the tableau or waste onto another tableau pile or foundation.
* **Undo Button** (top-right): Revert the last draw or card move.
* **Play Again**: After winning, click the “Play Again” button to restart with the same difficulty.

### Objective

Move all cards to the four foundation piles (one for each suit) in ascending order (Ace → King).

## Code Structure

* **`select_difficulty()`**: Displays difficulty selection menu.
* **`make_card_faces()`**: Generates card face images at runtime.
* **`Card` class**: Represents individual playing cards.
* **`create_deck()`**: Builds and shuffles a standard 52-card deck.
* **`SolitaireGame` class**: Manages game state, rendering, input, animations, win detection, and undo history.
* **`run_game()`**: Main loop handling events, updates, and drawing.

All logic resides in `solitaire.py` for simplicity.

## Customization

* **Add Themes**: Extend the `THEMES` list and `THEME_CONFIG` dict with new color schemes.
* **Change Difficulty**: Modify `DIFFICULTY_SETTINGS` and `WASTE_DISPLAY` to support new modes.
* **Adjust Layout**: Tweak `WIDTH`, `HEIGHT`, and spacing constants for different screen sizes.

## License

This project is released under the MIT License.

---

