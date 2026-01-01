import pytest

import game.checkers as checkers
from util.globalconst import BLACK, WHITE, MAN, KING


# --- Mirror mapping (left-right) for your square index scheme ---------------

MIRROR = {
    # top row
    45: 48,
    46: 47,
    47: 46,
    48: 45,
    # next row
    39: 42,
    40: 41,
    41: 40,
    42: 39,
    # next row
    34: 37,
    35: 36,
    36: 35,
    37: 34,
    # next row
    28: 31,
    29: 30,
    30: 29,
    31: 28,
    # next row
    23: 26,
    24: 25,
    25: 24,
    26: 23,
    # next row
    17: 20,
    18: 19,
    19: 18,
    20: 17,
    # next row
    12: 15,
    13: 14,
    14: 13,
    15: 12,
    # bottom row
    6: 9,
    7: 8,
    8: 7,
    9: 6,
}


def mirror_placements(placements: dict[int, int]) -> dict[int, int]:
    """
    Mirror every occupied square left-right while preserving piece values.
    """
    out = {}
    for sq, piece in placements.items():
        if sq not in MIRROR:
            raise KeyError(f"Square {sq} has no MIRROR mapping. (Not a playable index?)")
        out[MIRROR[sq]] = piece
    return out


def setup_position(game: checkers.Checkers, to_move: int, placements: dict[int, int]):
    board = game.curr_state
    board.clear()
    board.to_move = to_move
    for idx, piece in placements.items():
        board.squares[idx] = piece
    return board


# --- Small positions (4–6 pieces) ------------------------------------------
# Goal: cover quiet moves, captures, multi-jumps, kings, edge/corner proximity.

POSITIONS = [
    dict(
        name="quiet_moves_4_pieces",
        to_move=BLACK,
        placements={
            12: BLACK | MAN,
            15: BLACK | MAN,
            41: WHITE | MAN,
            42: WHITE | MAN,
        },
    ),
    dict(
        name="forced_capture_4_pieces_black",
        to_move=BLACK,
        placements={
            6: BLACK | MAN,
            12: WHITE | MAN,  # enables 6x12->18
            29: WHITE | MAN,  # irrelevant extra piece far away
            31: BLACK | MAN,  # irrelevant extra piece far away
        },
    ),
    dict(
        name="forced_capture_4_pieces_white",
        to_move=WHITE,
        placements={
            41: WHITE | MAN,
            36: BLACK | MAN,  # enables 41x36->31
            18: BLACK | MAN,
            20: WHITE | MAN,
        },
    ),
    dict(
        name="multijump_compact_5_pieces_black",
        to_move=BLACK,
        placements={
            6: BLACK | MAN,
            12: WHITE | MAN,
            23: WHITE | MAN,  # often yields 6x12->18x23->28 line
            40: WHITE | MAN,  # extra distractor
            42: BLACK | MAN,  # extra distractor
        },
    ),
    dict(
        name="king_center_4_pieces",
        to_move=BLACK,
        placements={
            28: BLACK | KING,
            23: WHITE | MAN,  # capture option
            34: WHITE | MAN,  # capture option
            15: WHITE | MAN,  # distractor
        },
    ),
    dict(
        name="edge_pressure_6_pieces",
        to_move=WHITE,
        placements={
            45: WHITE | KING,  # near top edge
            39: BLACK | MAN,
            40: BLACK | MAN,
            9: BLACK | KING,  # near bottom edge
            12: WHITE | MAN,
            15: WHITE | MAN,
        },
    ),
]


# Depths: keep modest so tests stay fast and deterministic.
DEPTHS = [2, 4]


@pytest.mark.parametrize("case", POSITIONS, ids=lambda c: c["name"])
def test_mirror_symmetry_perft(case):
    game = checkers.Checkers()

    placements = case["placements"]
    placements_m = mirror_placements(placements)

    board = setup_position(game, case["to_move"], placements)
    board_m = setup_position(game, case["to_move"], placements_m)

    for d in DEPTHS:
        a = game.perft(d, board)
        b = game.perft(d, board_m)
        assert a == b, (
            f"Perft mirror mismatch at depth={d}\n"
            f"orig placements={placements}\n"
            f"mirr placements={placements_m}\n"
            f"orig={a} mirr={b}"
        )
