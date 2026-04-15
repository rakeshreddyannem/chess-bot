# Chess Bot Arena - Custom Chess Engine

This repository contains a purely Python-based, algorithmic Chess Bot designed for the **Chess Bot Arena** competition. The bot operates entirely independently without relying on any pre-built engines (like Stockfish) or external APIs, ensuring full compliance with competition rules.

## Core Features 🧠

* **Algorithm**: The core decision-making is powered by the **Minimax algorithm** enhanced with **Alpha-Beta Pruning** to efficiently evaluate deep variations without exhausting computational resources.
* **Evaluation**: The bot relies on a comprehensive Evaluation Function that calculates:
  * **Material Advantage** (Standard piece values: P=100, N=320, B=330, R=500, Q=900, K=20000).
  * **Positional Understanding** through highly tuned **Piece-Square Tables (PST)** which guide pieces to mathematically optimal active squares early in the game.
* **Move Ordering**: To maximize Alpha-Beta cutoffs, the engine evaluates captures before quiet moves, drastically boosting search speed.
* **Time Management**: The bot uses **Iterative Deepening**, which means it searches depth 1, then depth 2, then depth 3, continuously updating its \"best move\" guess. Since the competition has a strict `4.0 second` time limit per move, Iterative Deepening guarantees the bot will immediately return the best move found once 80% of its time limit has elapsed. 
* **Zero Dependencies**: Pure Python logic—no external dependencies, networking, or installations required.

## Specifications ⚙️

As per the competition rules, this engine is entirely headless (no UI/GUI). It acts as a standard input/output backend interface:
* **Input**: Accepts board states exclusively in standard **FEN (Forsyth-Edwards Notation)** format.
* **Output**: Strictly responds with universally parsable **UCI (Universal Chess Interface)** strings (e.g., `e2e4`, `g1f3`, `e1g1` for kingside castling).
* **Legality**: Fully handles advanced chess implementations like **En Passant**, **Castling rights**, and blocks all pseudo-legal moves that would inherently leave the king in check.

## Testing & Usage 🧪

A test suite is included to verify the logic and validity of the bot under competition time constraints.

To run the automated tests against predefined critical positions (e.g. Scholar's mate, Back-rank mate):
```bash
python test_chess_bot.py
```

The tester will process predefined Checkmates and Captures, validating move legality and execution speed. It also features a real-time prompt to submit a custom FEN.

---

*Good luck at the Chess Bot Arena!* ♟️
