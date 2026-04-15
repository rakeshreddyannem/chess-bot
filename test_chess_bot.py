"""
Quick tester for chess_bot.py
Run: python test_chess_bot.py
"""
from chess_bot import get_best_move, Board

TEST_POSITIONS = [
    # Starting position
    ("Starting position",
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),

    # Scholar's mate threat – White should find Qxf7#
    ("Scholar's mate in 1",
     "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 1"),

    # Back-rank mate – White Rook can deliver mate
    ("Back-rank mate in 1",
     "6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1"),

    # Black to move – simple material win
    ("Black captures queen",
     "rnb1kbnr/pppp1ppp/8/4p3/4P1q1/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1"),
]

def main():
    print("=" * 55)
    print("       CHESS BOT ARENA – TEST SUITE")
    print("=" * 55)
    for name, fen in TEST_POSITIONS:
        import time
        t0 = time.time()
        move = get_best_move(fen, time_limit=3.0)
        elapsed = time.time() - t0
        board = Board.from_fen(fen)
        legal = board.generate_moves()
        legal_uci = []
        for fr,to,p in legal:
            u = Board.idx_to_alg(fr)+Board.idx_to_alg(to)
            if p and p != 'castle': u+=p.lower()
            legal_uci.append(u)
        status = "✓ LEGAL" if move in legal_uci or move=="0000" else "✗ ILLEGAL"
        print(f"\n[{name}]")
        print(f"  FEN   : {fen}")
        print(f"  Move  : {move}  ({elapsed:.2f}s)  {status}")
    print("\n" + "=" * 55)

    # Interactive mode
    print("\nEnter your own FEN (or 'quit' to exit):")
    while True:
        fen = input("FEN> ").strip()
        if fen.lower() in ('quit','exit','q'): break
        if not fen: continue
        import time
        t0 = time.time()
        move = get_best_move(fen, time_limit=3.5)
        print(f"Best move: {move}  ({time.time()-t0:.2f}s)")

if __name__ == "__main__":
    main()
