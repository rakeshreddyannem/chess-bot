"""
Chess Bot for Chess Bot Arena
Algorithm: Minimax with Alpha-Beta Pruning + Iterative Deepening
Evaluation: Material + Piece-Square Tables + Basic Positional Features
Input:  FEN string
Output: Best move in UCI format (e.g., e2e4)
"""

import time
import sys
from copy import deepcopy

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100,'n': -320,'b': -330,'r': -500,'q': -900,'k': -20000,
}

# Piece-Square Tables (from White's perspective; flipped for Black)
# Pawns
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_MID_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

PST = {
    'P': PAWN_TABLE, 'N': KNIGHT_TABLE, 'B': BISHOP_TABLE,
    'R': ROOK_TABLE, 'Q': QUEEN_TABLE,  'K': KING_MID_TABLE,
}

# ─────────────────────────────────────────────
#  BOARD REPRESENTATION
# ─────────────────────────────────────────────
class Board:
    """
    Internal board: list of 64 squares (rank 8 … rank 1, file a…h).
    index 0 = a8, index 7 = h8, index 56 = a1, index 63 = h1
    """
    def __init__(self):
        self.squares   = ['.'] * 64
        self.turn      = 'w'          # 'w' or 'b'
        self.castling  = set()        # 'K','Q','k','q'
        self.ep_square = None         # index or None
        self.halfmove  = 0
        self.fullmove  = 1

    # ── FEN parsing ──────────────────────────
    @classmethod
    def from_fen(cls, fen: str):
        b = cls()
        parts = fen.strip().split()
        rows = parts[0].split('/')
        idx = 0
        for row in rows:
            for ch in row:
                if ch.isdigit():
                    idx += int(ch)
                else:
                    b.squares[idx] = ch
                    idx += 1
        b.turn = parts[1] if len(parts) > 1 else 'w'
        castling_str = parts[2] if len(parts) > 2 else '-'
        b.castling = set(castling_str) - {'-'}
        ep_str = parts[3] if len(parts) > 3 else '-'
        b.ep_square = cls._sq(ep_str) if ep_str != '-' else None
        b.halfmove  = int(parts[4]) if len(parts) > 4 else 0
        b.fullmove  = int(parts[5]) if len(parts) > 5 else 1
        return b

    @staticmethod
    def _sq(alg: str) -> int:
        """Algebraic (e.g. 'e4') → index."""
        file = ord(alg[0]) - ord('a')
        rank = int(alg[1]) - 1
        return (7 - rank) * 8 + file

    @staticmethod
    def idx_to_alg(idx: int) -> str:
        file = idx % 8
        rank = 7 - (idx // 8)
        return chr(ord('a') + file) + str(rank + 1)

    def piece_at(self, idx): return self.squares[idx]

    def is_white(self, p): return p.isupper()
    def is_black(self, p): return p.islower()
    def color(self, p):    return 'w' if p.isupper() else 'b'

    # ── Move Generation ──────────────────────
    def generate_moves(self):
        moves = []
        for idx in range(64):
            p = self.squares[idx]
            if p == '.' or self.color(p) != self.turn:
                continue
            pt = p.upper()
            if   pt == 'P': moves += self._pawn_moves(idx, p)
            elif pt == 'N': moves += self._knight_moves(idx)
            elif pt == 'B': moves += self._slide_moves(idx, [(-1,-1),(-1,1),(1,-1),(1,1)])
            elif pt == 'R': moves += self._slide_moves(idx, [(-1,0),(1,0),(0,-1),(0,1)])
            elif pt == 'Q': moves += self._slide_moves(idx, [(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)])
            elif pt == 'K': moves += self._king_moves(idx)
        # Filter illegal (leaves own king in check)
        legal = []
        for m in moves:
            b2 = self.apply_move(m)
            if not b2._in_check(self.turn):
                legal.append(m)
        return legal

    def _rank(self, idx): return idx // 8
    def _file(self, idx): return idx % 8
    def _idx(self, r, f): return r * 8 + f

    def _pawn_moves(self, idx, p):
        moves = []
        r, f = self._rank(idx), self._file(idx)
        dir_ = -1 if p == 'P' else 1
        promo_rank = 0 if p == 'P' else 7
        start_rank = 6 if p == 'P' else 1

        # Single push
        nr = r + dir_
        if 0 <= nr <= 7 and self.squares[self._idx(nr, f)] == '.':
            if nr == promo_rank:
                for pp in ('Q','R','B','N'):
                    moves.append((idx, self._idx(nr,f), pp if p=='P' else pp.lower()))
            else:
                moves.append((idx, self._idx(nr,f), None))
            # Double push
            if r == start_rank:
                nr2 = r + 2*dir_
                if self.squares[self._idx(nr2, f)] == '.':
                    moves.append((idx, self._idx(nr2,f), None))

        # Captures
        for df in (-1, 1):
            nf = f + df
            if 0 <= nf <= 7 and 0 <= nr <= 7:
                target_idx = self._idx(nr, nf)
                target = self.squares[target_idx]
                enemy = self.is_black(target) if p == 'P' else self.is_white(target)
                if enemy or target_idx == self.ep_square:
                    if nr == promo_rank:
                        for pp in ('Q','R','B','N'):
                            moves.append((idx, target_idx, pp if p=='P' else pp.lower()))
                    else:
                        moves.append((idx, target_idx, None))
        return moves

    def _knight_moves(self, idx):
        moves = []
        r, f = self._rank(idx), self._file(idx)
        for dr, df in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nf = r+dr, f+df
            if 0<=nr<=7 and 0<=nf<=7:
                to = self._idx(nr, nf)
                t = self.squares[to]
                if t == '.' or self.color(t) != self.turn:
                    moves.append((idx, to, None))
        return moves

    def _slide_moves(self, idx, dirs):
        moves = []
        r, f = self._rank(idx), self._file(idx)
        for dr, df in dirs:
            nr, nf = r+dr, f+df
            while 0<=nr<=7 and 0<=nf<=7:
                to = self._idx(nr, nf)
                t = self.squares[to]
                if t == '.':
                    moves.append((idx, to, None))
                elif self.color(t) != self.turn:
                    moves.append((idx, to, None))
                    break
                else:
                    break
                nr += dr; nf += df
        return moves

    def _king_moves(self, idx):
        moves = []
        r, f = self._rank(idx), self._file(idx)
        for dr in (-1,0,1):
            for df in (-1,0,1):
                if dr==0 and df==0: continue
                nr, nf = r+dr, f+df
                if 0<=nr<=7 and 0<=nf<=7:
                    to = self._idx(nr,nf)
                    t = self.squares[to]
                    if t=='.' or self.color(t)!=self.turn:
                        moves.append((idx,to,None))
        # Castling
        if self.turn == 'w' and r==7 and f==4:
            if 'K' in self.castling and self.squares[63]=='R' and self.squares[62]=='.' and self.squares[61]=='.':
                if not self._sq_attacked(60,'b') and not self._sq_attacked(61,'b') and not self._sq_attacked(62,'b'):
                    moves.append((60,62,'castle'))
            if 'Q' in self.castling and self.squares[56]=='R' and self.squares[57]=='.' and self.squares[58]=='.' and self.squares[59]=='.':
                if not self._sq_attacked(60,'b') and not self._sq_attacked(59,'b') and not self._sq_attacked(58,'b'):
                    moves.append((60,58,'castle'))
        if self.turn == 'b' and r==0 and f==4:
            if 'k' in self.castling and self.squares[7]=='r' and self.squares[6]=='.' and self.squares[5]=='.':
                if not self._sq_attacked(4,'w') and not self._sq_attacked(5,'w') and not self._sq_attacked(6,'w'):
                    moves.append((4,6,'castle'))
            if 'q' in self.castling and self.squares[0]=='r' and self.squares[1]=='.' and self.squares[2]=='.' and self.squares[3]=='.':
                if not self._sq_attacked(4,'w') and not self._sq_attacked(3,'w') and not self._sq_attacked(2,'w'):
                    moves.append((4,2,'castle'))
        return moves

    # ── Apply Move ───────────────────────────
    def apply_move(self, move):
        b = Board()
        b.squares   = self.squares[:]
        b.turn      = self.turn
        b.castling  = set(self.castling)
        b.ep_square = None
        b.halfmove  = self.halfmove + 1
        b.fullmove  = self.fullmove + (1 if self.turn=='b' else 0)

        fr, to, flag = move
        piece = b.squares[fr]
        b.squares[fr] = '.'

        # En passant capture
        if piece.upper()=='P' and to==self.ep_square:
            ep_dir = 1 if piece=='P' else -1
            b.squares[to + ep_dir*8] = '.'

        # Set ep square on double pawn push
        if piece.upper()=='P' and abs(fr-to)==16:
            b.ep_square = (fr+to)//2

        # Promotion
        if flag and flag != 'castle':
            b.squares[to] = flag
        else:
            b.squares[to] = piece

        # Castling rook
        if flag == 'castle':
            if to == 62: b.squares[61]=b.squares[63]; b.squares[63]='.'
            if to == 58: b.squares[59]=b.squares[56]; b.squares[56]='.'
            if to ==  6: b.squares[5] =b.squares[7];  b.squares[7] ='.'
            if to ==  2: b.squares[3] =b.squares[0];  b.squares[0] ='.'

        # Update castling rights
        if piece=='K': b.castling -= {'K','Q'}
        if piece=='k': b.castling -= {'k','q'}
        if fr==63 or to==63: b.castling -= {'K'}
        if fr==56 or to==56: b.castling -= {'Q'}
        if fr==7  or to==7:  b.castling -= {'k'}
        if fr==0  or to==0:  b.castling -= {'q'}

        b.turn = 'b' if self.turn=='w' else 'w'
        return b

    # ── Check Detection ──────────────────────
    def _sq_attacked(self, idx, by_color):
        """Is square idx attacked by by_color?"""
        r, f = self._rank(idx), self._file(idx)
        # Knights
        for dr,df in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr,nf=r+dr,f+df
            if 0<=nr<=7 and 0<=nf<=7:
                p=self.squares[self._idx(nr,nf)]
                if p!='.':
                    if p.upper()=='N' and self.color(p)==by_color: return True
        # Sliding (rook/queen/bishop/queen)
        for dirs, types in [
            ([(-1,0),(1,0),(0,-1),(0,1)], 'RQ'),
            ([(-1,-1),(-1,1),(1,-1),(1,1)], 'BQ'),
        ]:
            for dr,df in dirs:
                nr,nf=r+dr,f+df
                while 0<=nr<=7 and 0<=nf<=7:
                    p=self.squares[self._idx(nr,nf)]
                    if p!='.':
                        if p.upper() in types and self.color(p)==by_color: return True
                        break
                    nr+=dr; nf+=df
        # King
        for dr in (-1,0,1):
            for df in (-1,0,1):
                if dr==0 and df==0: continue
                nr,nf=r+dr,f+df
                if 0<=nr<=7 and 0<=nf<=7:
                    p=self.squares[self._idx(nr,nf)]
                    if p!='.':
                        if p.upper()=='K' and self.color(p)==by_color: return True
        # Pawns
        pawn_dirs = [(1,-1),(1,1)] if by_color=='w' else [(-1,-1),(-1,1)]
        for dr,df in pawn_dirs:
            nr,nf=r+dr,f+df
            if 0<=nr<=7 and 0<=nf<=7:
                p=self.squares[self._idx(nr,nf)]
                if p!='.':
                    if p.upper()=='P' and self.color(p)==by_color: return True
        return False

    def _in_check(self, color):
        king = 'K' if color=='w' else 'k'
        for i,p in enumerate(self.squares):
            if p==king:
                opp = 'b' if color=='w' else 'w'
                return self._sq_attacked(i, opp)
        return False

    def is_checkmate(self):
        return self._in_check(self.turn) and len(self.generate_moves())==0

    def is_stalemate(self):
        return not self._in_check(self.turn) and len(self.generate_moves())==0

# ─────────────────────────────────────────────
#  EVALUATION
# ─────────────────────────────────────────────
def evaluate(board: Board) -> int:
    score = 0
    for idx, p in enumerate(board.squares):
        if p == '.': continue
        val = PIECE_VALUES[p]
        pt  = p.upper()
        if pt in PST:
            tbl_idx = idx if p.isupper() else (56 - (idx//8)*8 + idx%8)  # flip for black
            tbl_idx = max(0, min(63, tbl_idx))
            pos_val = PST[pt][tbl_idx]
            if p.islower(): pos_val = -pos_val
        else:
            pos_val = 0
        score += val + pos_val
    return score

# ─────────────────────────────────────────────
#  MOVE ORDERING  (captures first)
# ─────────────────────────────────────────────
def order_moves(board, moves):
    def score(m):
        fr, to, _ = m
        target = board.squares[to]
        if target != '.':
            return -(PIECE_VALUES.get(target.upper(), 0))
        return 0
    return sorted(moves, key=score)

# ─────────────────────────────────────────────
#  MINIMAX + ALPHA-BETA
# ─────────────────────────────────────────────
def alphabeta(board, depth, alpha, beta, maximizing, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise TimeoutError()

    if depth == 0:
        return evaluate(board), None

    moves = board.generate_moves()
    if not moves:
        if board._in_check(board.turn):
            return -99999 if board.turn == 'w' else 99999, None
        return 0, None

    moves = order_moves(board, moves)
    best_move = moves[0]

    if maximizing:
        best = -float('inf')
        for m in moves:
            nb = board.apply_move(m)
            val, _ = alphabeta(nb, depth-1, alpha, beta, False, start_time, time_limit)
            if val > best:
                best, best_move = val, m
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best, best_move
    else:
        best = float('inf')
        for m in moves:
            nb = board.apply_move(m)
            val, _ = alphabeta(nb, depth-1, alpha, beta, True, start_time, time_limit)
            if val < best:
                best, best_move = val, m
            beta = min(beta, best)
            if beta <= alpha: break
        return best, best_move

# ─────────────────────────────────────────────
#  ITERATIVE DEEPENING
# ─────────────────────────────────────────────
def get_best_move(fen: str, time_limit: float = 3.5) -> str:
    board = Board.from_fen(fen)
    start = time.time()
    maximizing = (board.turn == 'w')

    best_move = None
    # Always have a fallback
    legal = board.generate_moves()
    if not legal:
        return "0000"  # No legal moves (shouldn't happen in valid position)
    best_move = legal[0]

    for depth in range(1, 20):
        try:
            _, move = alphabeta(board, depth, -float('inf'), float('inf'), maximizing, start, time_limit)
            if move:
                best_move = move
            elapsed = time.time() - start
            # Stop searching if we're past 80% of time budget
            if elapsed > time_limit * 0.8:
                break
        except TimeoutError:
            break

    if best_move is None:
        return "0000"

    fr, to, promo = best_move
    uci = Board.idx_to_alg(fr) + Board.idx_to_alg(to)
    if promo and promo != 'castle':
        uci += promo.lower()
    return uci

# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Accept FEN from command-line argument or stdin
    if len(sys.argv) > 1:
        fen = " ".join(sys.argv[1:])
    else:
        fen = input("Enter FEN: ").strip()

    move = get_best_move(fen, time_limit=3.5)
    print(move)
