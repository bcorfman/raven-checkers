import pytest

import game.checkers as checkers
from util.globalconst import BLACK, WHITE, MAN, KING, FREE


# --- Helpers ---------------------------------------------------------------


def setup_position(game: checkers.Checkers, to_move: int, placements: dict[int, int]):
    """
    placements: {square_index: piece_int}, where piece_int is e.g. BLACK|MAN, WHITE|KING, etc.
    """
    board = game.curr_state
    board.clear()
    board.to_move = to_move
    for idx, piece in placements.items():
        board.squares[idx] = piece
    return board


def snapshot(board):
    """Exact snapshot of state that should be preserved by make+undo."""
    return (tuple(board.squares), board.to_move)


def assert_roundtrip_for_all_legal_moves(game: checkers.Checkers, board):
    """
    For every legal move from this position:
      make_move -> undo_move -> board returns to identical snapshot.
    """
    before = snapshot(board)
    moves = game.legal_moves(board)

    # If you expect moves, enforce it at the test-case level; otherwise allow terminal positions.
    for mv in moves:
        board.make_move(mv, notify=False, undo=False)

        # Optional: ensure the board actually changed (helps detect no-op moves).
        assert snapshot(board) != before, f"Move produced no state change: {mv.affected_squares}"

        board.undo_move(mv, notify=False, redo=False)
        after = snapshot(board)
        assert after == before, f"make/undo failed round-trip for move: {mv.affected_squares}"


# --- Positions -------------------------------------------------------------
# Keep these small (4-8 pieces). Include nasties:
# - quiet moves
# - single capture
# - multi-jump
# - king moves/captures
# - crowning moves/captures (because your Move record encodes KING at destination)

POSITIONS = [
    dict(
        name="quiet_moves_black_two_men",
        to_move=BLACK,
        placements={
            12: BLACK | MAN,
            13: BLACK | MAN,
        },
        expect_moves=True,
    ),
    dict(
        name="quiet_moves_white_two_men",
        to_move=WHITE,
        placements={
            41: WHITE | MAN,
            40: WHITE | MAN,
        },
        expect_moves=True,
    ),
    dict(
        name="single_capture_black",
        to_move=BLACK,
        placements={
            6: BLACK | MAN,
            12: WHITE | MAN,  # enables 6x12->18
        },
        expect_moves=True,
    ),
    dict(
        name="single_capture_white",
        to_move=WHITE,
        placements={
            41: WHITE | MAN,
            36: BLACK | MAN,  # enables 41x36->31
        },
        expect_moves=True,
    ),
    dict(
        name="multi_jump_black_compact",
        to_move=BLACK,
        placements={
            6: BLACK | MAN,
            12: WHITE | MAN,
            23: WHITE | MAN,  # typical 6x12->18x23->28 shape
        },
        expect_moves=True,
    ),
    dict(
        name="multi_jump_white_compact",
        to_move=WHITE,
        placements={
            41: WHITE | MAN,
            36: BLACK | MAN,
            25: BLACK | MAN,  # matches your existing double-jump style
        },
        expect_moves=True,
    ),
    dict(
        name="king_quiet_moves_center_black",
        to_move=BLACK,
        placements={
            28: BLACK | KING,
        },
        expect_moves=True,
    ),
    dict(
        name="king_two_capture_options_black",
        to_move=BLACK,
        placements={
            28: BLACK | KING,
            23: WHITE | MAN,  # 28x23->18
            34: WHITE | MAN,  # 28x34->40
        },
        expect_moves=True,
    ),
    dict(
        name="black_crowning_by_move",
        to_move=BLACK,
        placements={
            39: BLACK | MAN,  # your existing crowning move is 39->45 -> KING
        },
        expect_moves=True,
    ),
    dict(
        name="white_crowning_by_move",
        to_move=WHITE,
        placements={
            15: WHITE | MAN,  # your existing crowning move is 15->9 -> KING
        },
        expect_moves=True,
    ),
    # Terminal/block position (roundtrip should still work even though there are no moves)
    dict(
        name="terminal_block_no_moves",
        to_move=BLACK,
        placements={
            35: WHITE | KING,
            40: WHITE | MAN,
            39: BLACK | MAN,
            45: BLACK | KING,
        },
        expect_moves=False,
    ),
]


@pytest.mark.parametrize("case", POSITIONS, ids=lambda c: c["name"])
def test_make_undo_roundtrip_for_all_moves(case):
    game = checkers.Checkers()
    board = setup_position(game, case["to_move"], case["placements"])

    moves = game.legal_moves(board)
    if case["expect_moves"]:
        assert moves, "Expected at least one legal move for this position."

    # The actual round-trip check
    assert_roundtrip_for_all_legal_moves(game, board)
