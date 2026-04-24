# Chess Bot Arena - Custom Chess Engine

Pure Python chess bot for a competition runner that sends one FEN string and expects one legal UCI move.

## Competition Contract

- Input: one standard FEN position.
- Output: exactly one UCI move on stdout, for example `e2e4`, `g1f3`, or `e7e8q`.
- Time limit: default search budget is `3.5` seconds, leaving margin under the 4 second rule.
- Dependencies: none. No Stockfish, external engines, APIs, or network calls.
- Failure mode: invalid or no-move positions return `0000` instead of crashing.

## Files

- `Rakesh_Reddy.py` - upload this one file to the Google Form. It supports `import Rakesh_Reddy`, `next_move(fen)`, and direct CLI execution.
- `chess_bot.py` - development copy of the same engine.
- `A.V. Rakesh Reddy.py` - older named copy kept for reference.
- `test_chess_bot.py` - local legality, timing, and CLI-output checks.

## Run

Command-line FEN:

```bash
python Rakesh_Reddy.py "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
```

Pipe FEN through stdin:

```bash
echo "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" | python Rakesh_Reddy.py
```

The default output is submission-safe: only the move is printed. For local diagnostics, use stderr-only timing:

```bash
python Rakesh_Reddy.py --debug "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
```

## Test

```bash
python test_chess_bot.py
```

For manual FEN experiments after the automated checks:

```bash
python test_chess_bot.py --interactive
```

## Engine Summary

The bot uses legal move generation, minimax with alpha-beta pruning, iterative deepening, material scoring, piece-square tables, and capture-first move ordering. It handles castling, promotion, en passant, check filtering, checkmate, and stalemate without using a pre-built chess engine.
