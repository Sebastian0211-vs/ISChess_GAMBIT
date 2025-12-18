"""evaluation.py

Static evaluation for the ISChess bot.

Design goals
- Fast: called thousands of times inside alpha-beta.
- Stable: avoid overly noisy heuristics.
- Strong: tapered (middlegame/endgame) evaluation with pawn structure + passed pawns.

Assumptions (your current project)
- 2 players only: colors 'w' and 'b'.
- `board` is a numpy 2D array (typically 8x8) but bots receive the *string board*.
- Each cell is one of:
    - '' / None / 'X' / 'XX' (empty / blocked)
    - a string like 'pw', 'kb', ... (piece + color)
    - OR (when used from GUI side) a Piece object with `.type` and `.color`

Usage
    from evaluation import evaluate
    score = evaluate(board, my_color='w')

Score convention
- Positive => good for my_color
- Negative => good for opponent
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

# -----------------------------------------------------------------------------
# Helpers: normalize board cell representation
# -----------------------------------------------------------------------------


def piece_type_color(cell: Any) -> Tuple[Optional[str], Optional[str]]:
    """Return (ptype, color) for a cell.

    Supports:
      - Piece objects (cell.type, cell.color)
      - strings / numpy.str_ like 'pw', 'kb'
      - empty markers: '', None, 'X', 'XX'

    Returns (None, None) if empty or invalid.
    """
    if cell is None:
        return None, None

    # Empty / blocked markers used in the repo
    if cell == "" or cell == "X" or cell == "XX":
        return None, None

    # Piece object case
    if hasattr(cell, "type") and hasattr(cell, "color"):
        return getattr(cell, "type"), getattr(cell, "color")

    # String / numpy.str_ case
    s = str(cell)
    if len(s) < 2:
        return None, None
    ptype, col = s[0], s[1]
    if ptype not in ("p", "n", "b", "r", "q", "k"):
        return None, None
    if col not in ("w", "b"):
        return None, None
    return ptype, col


# -----------------------------------------------------------------------------
# Material (centipawns)
# -----------------------------------------------------------------------------

# Slightly different MG/EG values help conversion.
PIECE_VALUE_MG = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}
PIECE_VALUE_EG = {"p": 120, "n": 310, "b": 320, "r": 520, "q": 880, "k": 0}

BISHOP_PAIR_BONUS_MG = 30
BISHOP_PAIR_BONUS_EG = 50


# -----------------------------------------------------------------------------
# Phase (tapered eval)
# -----------------------------------------------------------------------------

PHASE_WEIGHT = {"q": 4, "r": 2, "b": 1, "n": 1}
PHASE_MAX = 4 * 2 + 2 * 4 + 1 * 4  # 24


def compute_phase(board) -> int:
    """Return phase in [0, PHASE_MAX]. Higher => more middlegame."""
    phase = 0
    h, w = board.shape
    for y in range(h):
        for x in range(w):
            ptype, _ = piece_type_color(board[y, x])
            if ptype is None:
                continue
            wt = PHASE_WEIGHT.get(ptype)
            if wt:
                phase += wt
    return max(0, min(PHASE_MAX, phase))


# -----------------------------------------------------------------------------
# Piece-Square Tables (PST)
# -----------------------------------------------------------------------------

# Indexing: PST[y][x] with y=0 top row, y=7 bottom row.
# Since your engine rotates the board for the player, you do NOT mirror.

PAWN_PST_MG = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [10, 10, 10, 10, 10, 10, 10, 10],
    [20, 20, 20, 20, 20, 20, 20, 20],
    [30, 30, 30, 30, 30, 30, 30, 30],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [60, 60, 60, 60, 60, 60, 60, 60],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

PAWN_PST_EG = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [15, 15, 15, 15, 15, 15, 15, 15],
    [30, 30, 30, 30, 30, 30, 30, 30],
    [45, 45, 45, 45, 45, 45, 45, 45],
    [60, 60, 60, 60, 60, 60, 60, 60],
    [80, 80, 80, 80, 80, 80, 80, 80],
    [110, 110, 110, 110, 110, 110, 110, 110],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

KNIGHT_PST_MG = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

KNIGHT_PST_EG = [
    [-40, -30, -20, -20, -20, -20, -30, -40],
    [-30, -10, 0, 0, 0, 0, -10, -30],
    [-20, 0, 10, 12, 12, 10, 0, -20],
    [-20, 5, 12, 15, 15, 12, 5, -20],
    [-20, 0, 12, 15, 15, 12, 0, -20],
    [-20, 5, 10, 12, 12, 10, 5, -20],
    [-30, -10, 0, 5, 5, 0, -10, -30],
    [-40, -30, -20, -20, -20, -20, -30, -40],
]

BISHOP_PST_MG = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

BISHOP_PST_EG = [
    [-10, -5, -5, -5, -5, -5, -5, -10],
    [-5, 5, 0, 0, 0, 0, 5, -5],
    [-5, 0, 10, 10, 10, 10, 0, -5],
    [-5, 10, 10, 15, 15, 10, 10, -5],
    [-5, 0, 15, 15, 15, 15, 0, -5],
    [-5, 10, 10, 10, 10, 10, 10, -5],
    [-5, 5, 0, 0, 0, 0, 5, -5],
    [-10, -5, -5, -5, -5, -5, -5, -10],
]

ROOK_PST_MG = [
    [0, 0, 0, 5, 5, 0, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

ROOK_PST_EG = [
    [0, 0, 5, 10, 10, 5, 0, 0],
    [0, 5, 10, 15, 15, 10, 5, 0],
    [0, 5, 10, 15, 15, 10, 5, 0],
    [0, 5, 10, 15, 15, 10, 5, 0],
    [0, 5, 10, 15, 15, 10, 5, 0],
    [0, 5, 10, 15, 15, 10, 5, 0],
    [0, 5, 10, 10, 10, 10, 5, 0],
    [0, 0, 5, 5, 5, 5, 0, 0],
]

QUEEN_PST_MG = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]

QUEEN_PST_EG = [
    [-10, -5, -5, -5, -5, -5, -5, -10],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [-5, 0, 5, 10, 10, 5, 0, -5],
    [-5, 0, 5, 10, 10, 5, 0, -5],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-10, -5, -5, -5, -5, -5, -5, -10],
]

KING_PST_MG = [
    [20, 30, 10, 0, 0, 10, 30, 20],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
]

KING_PST_EG = [
    [-50, -30, -20, -10, -10, -20, -30, -50],
    [-30, -10, 0, 10, 10, 0, -10, -30],
    [-20, 0, 15, 20, 20, 15, 0, -20],
    [-10, 10, 20, 30, 30, 20, 10, -10],
    [-10, 10, 20, 30, 30, 20, 10, -10],
    [-20, 0, 15, 20, 20, 15, 0, -20],
    [-30, -10, 0, 10, 10, 0, -10, -30],
    [-50, -30, -20, -10, -10, -20, -30, -50],
]

PST_MG = {
    "p": PAWN_PST_MG,
    "n": KNIGHT_PST_MG,
    "b": BISHOP_PST_MG,
    "r": ROOK_PST_MG,
    "q": QUEEN_PST_MG,
    "k": KING_PST_MG,
}

PST_EG = {
    "p": PAWN_PST_EG,
    "n": KNIGHT_PST_EG,
    "b": BISHOP_PST_EG,
    "r": ROOK_PST_EG,
    "q": QUEEN_PST_EG,
    "k": KING_PST_EG,
}


# -----------------------------------------------------------------------------
# Pawn structure + passed pawns
# -----------------------------------------------------------------------------

DOUBLED_PAWN_PENALTY_MG = 12
DOUBLED_PAWN_PENALTY_EG = 10
ISOLATED_PAWN_PENALTY_MG = 10
ISOLATED_PAWN_PENALTY_EG = 6

PASSED_BONUS_MG = [0, 5, 10, 20, 35, 60, 100, 0]
PASSED_BONUS_EG = [0, 10, 25, 45, 70, 110, 170, 0]


def pawn_structure_score(my_files, en_files) -> Tuple[int, int]:
    mg = 0
    eg = 0

    # Doubled pawns
    for f in range(8):
        if my_files[f] >= 2:
            mg -= DOUBLED_PAWN_PENALTY_MG * (my_files[f] - 1)
            eg -= DOUBLED_PAWN_PENALTY_EG * (my_files[f] - 1)
        if en_files[f] >= 2:
            mg += DOUBLED_PAWN_PENALTY_MG * (en_files[f] - 1)
            eg += DOUBLED_PAWN_PENALTY_EG * (en_files[f] - 1)

    def is_isolated(files, f: int) -> bool:
        left = files[f - 1] if f - 1 >= 0 else 0
        right = files[f + 1] if f + 1 < 8 else 0
        return files[f] > 0 and left == 0 and right == 0

    for f in range(8):
        if is_isolated(my_files, f):
            mg -= ISOLATED_PAWN_PENALTY_MG
            eg -= ISOLATED_PAWN_PENALTY_EG
        if is_isolated(en_files, f):
            mg += ISOLATED_PAWN_PENALTY_MG
            eg += ISOLATED_PAWN_PENALTY_EG

    return mg, eg


def is_passed_pawn_my(board, y: int, x: int, enemy_color: str) -> bool:
    """My pawns assumed to move 'forward' toward increasing y."""
    for fx in (x - 1, x, x + 1):
        if 0 <= fx < 8:
            for yy in range(y + 1, 8):
                qt, qc = piece_type_color(board[yy, fx])
                if qt == "p" and qc == enemy_color:
                    return False
    return True


def is_passed_pawn_enemy(board, y: int, x: int, my_color: str) -> bool:
    """Enemy pawns assumed to move toward decreasing y."""
    for fx in (x - 1, x, x + 1):
        if 0 <= fx < 8:
            for yy in range(y - 1, -1, -1):
                qt, qc = piece_type_color(board[yy, fx])
                if qt == "p" and qc == my_color:
                    return False
    return True


def passed_pawns_score(board, my_color: str, enemy_color: str) -> Tuple[int, int]:
    mg = 0
    eg = 0
    for y in range(8):
        for x in range(8):
            pt, pc = piece_type_color(board[y, x])
            if pt != "p":
                continue

            if pc == my_color:
                if is_passed_pawn_my(board, y, x, enemy_color):
                    mg += PASSED_BONUS_MG[y]
                    eg += PASSED_BONUS_EG[y]
            elif pc == enemy_color:
                if is_passed_pawn_enemy(board, y, x, my_color):
                    mg -= PASSED_BONUS_MG[7 - y]
                    eg -= PASSED_BONUS_EG[7 - y]

    return mg, eg


# -----------------------------------------------------------------------------
# King safety (cheap midgame only)
# -----------------------------------------------------------------------------


def king_pawn_shield_midgame(board, color: str, ky: int, kx: int) -> int:
    """Very cheap king safety: reward friendly pawns in front of king."""
    score = 0
    for dy, dx in ((1, -1), (1, 0), (1, 1)):
        y = ky + dy
        x = kx + dx
        if 0 <= y < 8 and 0 <= x < 8:
            pt, pc = piece_type_color(board[y, x])
            if pt == "p" and pc == color:
                score += 12
            else:
                score -= 8
    return score


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------


def evaluate(board, my_color: str) -> int:
    """Return a score in centipawns. Positive => good for `my_color`."""
    enemy_color = "b" if my_color == "w" else "w"

    phase = compute_phase(board)
    mgw = phase / PHASE_MAX
    egw = 1.0 - mgw

    mg = 0
    eg = 0

    my_bishops = 0
    en_bishops = 0

    my_pawns_by_file = [0] * 8
    en_pawns_by_file = [0] * 8

    my_king_pos: Optional[Tuple[int, int]] = None
    en_king_pos: Optional[Tuple[int, int]] = None

    # Material + PST (tapered)
    for y in range(8):
        for x in range(8):
            pt, pc = piece_type_color(board[y, x])
            if pt is None:
                continue

            sign = 1 if pc == my_color else -1

            if pt == "b":
                if sign == 1:
                    my_bishops += 1
                else:
                    en_bishops += 1

            if pt == "p":
                if sign == 1:
                    my_pawns_by_file[x] += 1
                else:
                    en_pawns_by_file[x] += 1

            if pt == "k":
                if sign == 1:
                    my_king_pos = (y, x)
                else:
                    en_king_pos = (y, x)

            mg += sign * (PIECE_VALUE_MG[pt] + PST_MG[pt][y][x])
            eg += sign * (PIECE_VALUE_EG[pt] + PST_EG[pt][y][x])

    # Bishop pair
    if my_bishops >= 2:
        mg += BISHOP_PAIR_BONUS_MG
        eg += BISHOP_PAIR_BONUS_EG
    if en_bishops >= 2:
        mg -= BISHOP_PAIR_BONUS_MG
        eg -= BISHOP_PAIR_BONUS_EG

    # Pawn structure
    ps_mg, ps_eg = pawn_structure_score(my_pawns_by_file, en_pawns_by_file)
    mg += ps_mg
    eg += ps_eg

    # Passed pawns
    pp_mg, pp_eg = passed_pawns_score(board, my_color, enemy_color)
    mg += pp_mg
    eg += pp_eg

    # King pawn shield (MG only)
    if my_king_pos is not None:
        mg += king_pawn_shield_midgame(board, my_color, my_king_pos[0], my_king_pos[1])
    if en_king_pos is not None:
        mg -= king_pawn_shield_midgame(board, enemy_color, en_king_pos[0], en_king_pos[1])

    return int(mg * mgw + eg * egw)
