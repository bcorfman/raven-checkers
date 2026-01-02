import itertools

import game.checkers as checkers
from util.globalconst import BLACK, MAN, WHITE


def _setup(game, to_move, placements):
    board = game.curr_state
    board.clear()
    board.to_move = to_move
    for idx, piece in placements.items():
        board.squares[idx] = piece
    return board


def _find_non_max_capture_position(game, to_move):
    """
    Find a small position where side-to-move has >=2 COMPLETED capture moves
    with different affected_squares lengths (different number of jumps).
    """

    board = game.curr_state
    valid = list(board.valid_squares)

    # Side-specific pools (biased to where forward captures are most likely).
    # WHITE moves "up" the index list (toward smaller indices), so start high.
    if to_move == WHITE:
        starts = [48, 47, 46, 45, 42, 41, 40, 39, 37, 36, 35, 34, 31, 30, 29, 28]
        opp_pool = [42, 41, 40, 39, 37, 36, 35, 34, 31, 30, 29, 28, 26, 25, 24, 23, 20, 19, 18, 17, 15, 14, 13, 12]
    else:
        # BLACK moves toward larger indices, so start low.
        starts = [6, 7, 8, 9, 12, 13, 14, 15, 17, 18, 19, 20, 23, 24, 25, 26]
        opp_pool = [12, 13, 14, 15, 17, 18, 19, 20, 23, 24, 25, 26, 28, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42]

    # Keep only legal squares for this engine.
    starts = [s for s in starts if s in valid]
    opp_pool = [s for s in opp_pool if s in valid]

    opp_color = WHITE if to_move == BLACK else BLACK

    # Try 3, then 4 opponent men. Forks for WHITE often need 4.
    for k in (3, 4):
        for me_sq in starts:
            pool = [s for s in opp_pool if s != me_sq]
            for opp_sqs in itertools.combinations(pool, k):
                placements = {me_sq: to_move | MAN}
                for o in opp_sqs:
                    placements[o] = opp_color | MAN

                # apply placements
                b = game.curr_state
                b.clear()
                b.to_move = to_move
                for idx, piece in placements.items():
                    b.squares[idx] = piece

                moves = game.legal_moves(b)
                captures = [m for m in moves if len(m.affected_squares) >= 3]
                if len(captures) < 2:
                    continue

                lengths = sorted({len(m.affected_squares) for m in captures})
                if len(lengths) >= 2:
                    return placements, lengths, captures

    return None, None, None


def test_non_max_capture_rule_black_search_finds_fork_and_keeps_shorter_line():
    game = checkers.Checkers()
    placements, lengths, captures = _find_non_max_capture_position(game, BLACK)

    assert placements is not None, "Search failed to find a branching capture fork for BLACK."

    # The key assertion: BOTH lengths exist in the move list returned by legal_moves().
    # (If an engine mistakenly enforces 'must take maximum captures', it may drop the shorter length.)
    cap_lengths = sorted({len(m.affected_squares) for m in captures})
    assert len(cap_lengths) >= 2, f"Expected >=2 capture lengths, got {cap_lengths}. placements={placements}"


def test_non_max_capture_rule_white_search_finds_fork_and_keeps_shorter_line():
    game = checkers.Checkers()
    placements, lengths, captures = _find_non_max_capture_position(game, WHITE)

    assert placements is not None, "Search failed to find a branching capture fork for WHITE."

    cap_lengths = sorted({len(m.affected_squares) for m in captures})
    assert len(cap_lengths) >= 2, f"Expected >=2 capture lengths, got {cap_lengths}. placements={placements}"
