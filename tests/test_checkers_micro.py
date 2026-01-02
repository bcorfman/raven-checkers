import pytest

import game.checkers as checkers
from util.globalconst import BLACK, KING, MAN, WHITE

# --- helpers ---------------------------------------------------------------


def setup_position(game: checkers.Checkers, to_move, placements: dict[int, int]):
    """
    placements: {square_index: (BLACK|WHITE) | (MAN|KING)}
    """
    board = game.curr_state
    board.clear()
    board.to_move = to_move
    squares = board.squares
    for idx, piece in placements.items():
        squares[idx] = piece
    return board


def snapshot(board):
    # Deep enough for your state: squares list + to_move.
    return (tuple(board.squares), board.to_move)


def assert_make_undo_roundtrip(game, board):
    """
    For every legal move from board:
      make_move -> undo_move -> board must be identical.
    This catches subtle state corruption (especially multi-jumps / kinging).
    """
    before = snapshot(board)
    moves = game.legal_moves(board)
    for mv in moves:
        board.make_move(mv, notify=False, undo=False)
        board.undo_move(mv, notify=False, redo=False)
        after = snapshot(board)
        assert after == before, f"make/undo failed to round-trip for move: {mv.affected_squares}"


# left-right mirror mapping using your row layout in test_checkers.py
_MIRROR = {
    # 45 46 47 48
    45: 48,
    46: 47,
    47: 46,
    48: 45,
    # 39 40 41 42
    39: 42,
    40: 41,
    41: 40,
    42: 39,
    # 34 35 36 37
    34: 37,
    35: 36,
    36: 35,
    37: 34,
    # 28 29 30 31
    28: 31,
    29: 30,
    30: 29,
    31: 28,
    # 23 24 25 26
    23: 26,
    24: 25,
    25: 24,
    26: 23,
    # 17 18 19 20
    17: 20,
    18: 19,
    19: 18,
    20: 17,
    # 12 13 14 15
    12: 15,
    13: 14,
    14: 13,
    15: 12,
    # 6  7  8  9
    6: 9,
    7: 8,
    8: 7,
    9: 6,
}


def mirror_placements(placements: dict[int, int]) -> dict[int, int]:
    return {_MIRROR[k]: v for k, v in placements.items()}


# --- micro scenarios -------------------------------------------------------

SCENARIOS = [
    # 1) Forced capture vs quiet moves (captures must suppress quiet moves)
    dict(
        name="forced_capture_suppresses_quiet_moves_black",
        to_move=BLACK,
        placements={
            6: BLACK | MAN,
            12: WHITE | MAN,  # enables capture 6x12->18
            17: BLACK | MAN,  # would have quiet moves if captures didn't exist
        },
        checks=["captures_only", "roundtrip", "perft1_invariant"],
    ),
    # 2) Same non-max capture idea but for WHITE.
    dict(
        name="non_max_capture_allowed_white",
        to_move=WHITE,
        placements={
            41: WHITE | MAN,
            36: BLACK | MAN,  # short capture: 41x36->31 (usually)
            35: BLACK | MAN,  # long line: 41x35->29 ...
            23: BLACK | MAN,  # ... then 29x23->17
        },
        checks=["both_short_and_long_capture_exist", "roundtrip", "perft1_invariant"],
    ),
    # 3) King capture branching: king should see captures in both directions.
    dict(
        name="king_has_two_capture_options_black",
        to_move=BLACK,
        placements={
            28: BLACK | KING,
            23: WHITE | MAN,  # allows 28x23->18
            34: WHITE | MAN,  # allows 28x34->40
        },
        checks=["at_least_two_captures", "roundtrip", "perft1_invariant"],
    ),
    # 4) A compact multi-jump for stability + symmetry checks
    #    (similar to your longer crowning tests, but without promotion).
    dict(
        name="stable_multijump_black",
        to_move=BLACK,
        placements={
            6: BLACK | MAN,
            12: WHITE | MAN,
            23: WHITE | MAN,  # yields 6x12->18x23->28 like your existing test
        },
        checks=["has_multijump", "roundtrip", "perft1_invariant", "mirror_perft_symmetry"],
    ),
]


@pytest.mark.parametrize("case", SCENARIOS, ids=lambda c: c["name"])
def test_micro_suite(case):
    game = checkers.Checkers()
    board = setup_position(game, case["to_move"], case["placements"])
    moves = game.legal_moves(board)

    # --- checks ------------------------------------------------------------

    if "captures_only" in case["checks"]:
        # captures are always 3+ affected squares; quiet moves are length 2 in this engine
        assert moves, "Expected at least one legal move"
        assert all(len(m.affected_squares) >= 3 for m in moves), "Expected captures only (no quiet moves)"

    if "both_short_and_long_capture_exist" in case["checks"]:
        # We expect a mix of 1-jump capture (3 affected squares) and multi-jump capture (>=5).
        lens = sorted({len(m.affected_squares) for m in moves})
        assert any(L == 3 for L in lens), f"Expected a 1-jump capture (len=3), got lengths: {lens}"
        assert any(L >= 5 for L in lens), f"Expected a multi-jump capture (len>=5), got lengths: {lens}"

    if "at_least_two_captures" in case["checks"]:
        assert len(moves) >= 2, f"Expected at least two distinct capture moves, got {len(moves)}"
        assert all(len(m.affected_squares) >= 3 for m in moves), "Expected capture moves"

    if "has_multijump" in case["checks"]:
        assert any(len(m.affected_squares) >= 5 for m in moves), "Expected at least one multi-jump capture"

    if "perft1_invariant" in case["checks"]:
        # Perft(1) must always equal number of legal root moves.
        assert game.perft(1, board) == len(moves)

    if "roundtrip" in case["checks"]:
        assert_make_undo_roundtrip(game, board)

    if "mirror_perft_symmetry" in case["checks"]:
        # Mirror the same position left-right; perft should match for same side to move.
        placements_m = mirror_placements(case["placements"])
        board_m = setup_position(game, case["to_move"], placements_m)
        # Keep depth modest—this is a “structure” invariant, not a performance test.
        assert game.perft(4, board) == game.perft(4, board_m)
