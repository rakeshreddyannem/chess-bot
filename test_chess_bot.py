"""
Quick tester for chess_bot.py.

Run:
    python test_chess_bot.py
    python test_chess_bot.py --interactive
"""
import subprocess
import sys
import time

from chess_bot import Board, get_best_move


TEST_POSITIONS = [
    (
        "Starting position",
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    ),
    (
        "Scholar's mate in 1",
        "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 1",
    ),
    (
        "Back-rank mate in 1",
        "6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1",
    ),
    (
        "Black captures queen",
        "rnb1kbnr/pppp1ppp/8/4p3/4P1q1/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1",
    ),
]


def legal_uci_moves(fen):
    board = Board.from_fen(fen)
    moves = []
    for fr, to, promo in board.generate_moves():
        uci = Board.idx_to_alg(fr) + Board.idx_to_alg(to)
        if promo and promo != "castle":
            uci += promo.lower()
        moves.append(uci)
    return moves


def run_position_tests():
    print("=" * 55)
    print("       CHESS BOT ARENA - TEST SUITE")
    print("=" * 55)
    failures = 0

    for name, fen in TEST_POSITIONS:
        start = time.time()
        move = get_best_move(fen, time_limit=3.5)
        elapsed = time.time() - start
        legal_moves = legal_uci_moves(fen)
        is_legal = move in legal_moves or (move == "0000" and not legal_moves)
        is_fast = elapsed < 4.0
        status = "PASS" if is_legal and is_fast else "FAIL"
        failures += 0 if status == "PASS" else 1

        print(f"\n[{name}]")
        print(f"  FEN   : {fen}")
        print(f"  Move  : {move}")
        print(f"  Time  : {elapsed:.2f}s")
        print(f"  Legal : {is_legal}")
        print(f"  Fast  : {is_fast}")
        print(f"  Result: {status}")

    return failures


def run_cli_output_test():
    fen = TEST_POSITIONS[0][1]
    completed = subprocess.run(
        [sys.executable, "chess_bot.py", fen],
        check=False,
        capture_output=True,
        text=True,
        timeout=4.2,
    )
    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    ok = completed.returncode == 0 and len(stdout_lines) == 1
    ok = ok and stdout_lines[0] in legal_uci_moves(fen)

    print("\n[CLI output]")
    print(f"  stdout lines: {len(stdout_lines)}")
    print(f"  stderr      : {completed.stderr.strip() or '(empty)'}")
    print(f"  Result      : {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def interactive_loop():
    print("\nEnter your own FEN (or 'quit' to exit):")
    while True:
        fen = input("FEN> ").strip()
        if fen.lower() in ("quit", "exit", "q"):
            break
        if not fen:
            continue
        start = time.time()
        move = get_best_move(fen, time_limit=3.5)
        print(f"Best move: {move} ({time.time() - start:.2f}s)")


def main():
    failures = run_position_tests()
    failures += run_cli_output_test()
    print("\n" + "=" * 55)
    print("PASS" if failures == 0 else f"FAILURES: {failures}")

    if "--interactive" in sys.argv[1:]:
        interactive_loop()

    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
