import game.checkers as checkers
from util.globalconst import BLACK, WHITE, MAN, KING, FREE

#   (white)
#            45  46  47  48
#          39  40  41  42
#            34  35  36  37
#          28  29  30  31
#            23  24  25  26
#          17  18  19  20
#            12  13  14  15
#          6   7   8   9
#   (black)


def test_black_man_single_jump():
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    squares[6] = BLACK | MAN
    squares[12] = WHITE | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[6, BLACK | MAN, FREE], [12, WHITE | MAN, FREE], [18, FREE, BLACK | MAN]]


def test_black_man_double_jump():
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    squares[6] = BLACK | MAN
    squares[12] = WHITE | MAN
    squares[23] = WHITE | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [
        [6, BLACK | MAN, FREE],
        [12, WHITE | MAN, FREE],
        [18, FREE, FREE],
        [23, WHITE | MAN, FREE],
        [28, FREE, BLACK | MAN],
    ]


def test_black_man_crown_king_on_jump_and_end_turn():
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    #   (white)
    #            45  46  47  48
    #          39  40  41  42
    #            34  35  36  37
    #          28  29  30  31
    #            23  24  25  26
    #          17  18  19  20
    #            12  13  14  15
    #          6   7   8   9
    #   (black)
    squares[12] = BLACK | MAN
    squares[18] = WHITE | MAN
    squares[30] = WHITE | MAN
    squares[41] = WHITE | MAN
    # set another man on 40 to test that crowning
    # move ends the turn
    squares[40] = WHITE | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [
        [12, BLACK | MAN, FREE],
        [18, WHITE | MAN, FREE],
        [24, FREE, FREE],
        [30, WHITE | MAN, FREE],
        [36, FREE, FREE],
        [41, WHITE | MAN, FREE],
        [46, FREE, BLACK | KING],
    ]


def test_black_man_crown_king_on_move():
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    squares[39] = BLACK | MAN
    squares[18] = WHITE | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[39, BLACK | MAN, FREE], [45, FREE, BLACK | KING]]


def test_black_king_optional_jump_diamond():
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    squares[13] = BLACK | KING
    squares[19] = WHITE | MAN
    squares[30] = WHITE | MAN
    squares[29] = WHITE | MAN
    squares[18] = WHITE | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [
        [13, BLACK | KING, FREE],
        [18, WHITE | MAN, FREE],
        [23, FREE, FREE],
        [29, WHITE | MAN, FREE],
        [35, FREE, FREE],
        [30, WHITE | MAN, FREE],
        [25, FREE, FREE],
        [19, WHITE | MAN, FREE],
        [13, FREE, BLACK | KING],
    ]
    assert moves[1].affected_squares == [
        [13, BLACK | KING, FREE],
        [19, WHITE | MAN, FREE],
        [25, FREE, FREE],
        [30, WHITE | MAN, FREE],
        [35, FREE, FREE],
        [29, WHITE | MAN, FREE],
        [23, FREE, FREE],
        [18, WHITE | MAN, FREE],
        [13, FREE, BLACK | KING],
    ]


def test_white_man_single_jump():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()
    squares[41] = WHITE | MAN
    squares[36] = BLACK | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[41, WHITE | MAN, FREE], [36, BLACK | MAN, FREE], [31, FREE, WHITE | MAN]]


def test_white_man_double_jump():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()
    squares[41] = WHITE | MAN
    squares[36] = BLACK | MAN
    squares[25] = BLACK | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [
        [41, WHITE | MAN, FREE],
        [36, BLACK | MAN, FREE],
        [31, FREE, FREE],
        [25, BLACK | MAN, FREE],
        [19, FREE, WHITE | MAN],
    ]


def test_white_man_crown_king_on_move():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()
    squares[15] = WHITE | MAN
    squares[36] = BLACK | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[15, WHITE | MAN, FREE], [9, FREE, WHITE | KING]]


def test_white_man_crown_king_on_jump():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()
    squares[41] = WHITE | MAN
    squares[36] = BLACK | MAN
    squares[25] = BLACK | MAN
    squares[13] = BLACK | KING
    # set another man on 10 to test that crowning
    # move ends the turn
    squares[12] = BLACK | KING
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [
        [41, WHITE | MAN, FREE],
        [36, BLACK | MAN, FREE],
        [31, FREE, FREE],
        [25, BLACK | MAN, FREE],
        [19, FREE, FREE],
        [13, BLACK | KING, FREE],
        [7, FREE, WHITE | KING],
    ]


def test_white_king_optional_jump_diamond():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()
    squares[13] = WHITE | KING
    squares[19] = BLACK | MAN
    squares[30] = BLACK | MAN
    squares[29] = BLACK | MAN
    squares[18] = BLACK | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [
        [13, WHITE | KING, FREE],
        [18, BLACK | MAN, FREE],
        [23, FREE, FREE],
        [29, BLACK | MAN, FREE],
        [35, FREE, FREE],
        [30, BLACK | MAN, FREE],
        [25, FREE, FREE],
        [19, BLACK | MAN, FREE],
        [13, FREE, WHITE | KING],
    ]
    assert moves[1].affected_squares == [
        [13, WHITE | KING, FREE],
        [19, BLACK | MAN, FREE],
        [25, FREE, FREE],
        [30, BLACK | MAN, FREE],
        [35, FREE, FREE],
        [29, BLACK | MAN, FREE],
        [23, FREE, FREE],
        [18, BLACK | MAN, FREE],
        [13, FREE, WHITE | KING],
    ]


# def test_double_corner_block_white_wins():
#     """ Final state of Pask's SOIC Chap 4, Diagram 44 (p. 79). White win. """
#     game = checkers.Checkers()
#     board = game.curr_state
#     board.to_move = BLACK
#     squares = board.squares
#     board.clear()
#     squares[35] = WHITE | KING
#     squares[39] = BLACK | MAN
#     squares[40] = WHITE | MAN
#     squares[45] = BLACK | KING
#     moves = game.legal_moves(board)
#     assert moves == []
#     assert board.utility(WHITE) == -100


def test_utility_func():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares

    code = sum(board.value[s] for s in squares)
    nwm = code % 16
    nwk = (code >> 4) % 16
    nbm = (code >> 8) % 16
    nbk = (code >> 12) % 16
    nm = nbm + nwm
    nk = nbk + nwk

    assert board._eval_cramp(squares) == 0
    assert board._eval_back_rank_guard(squares) == 0
    assert board._eval_double_corner(squares) == 0
    assert board._eval_center(squares) == 0
    assert board._eval_edge(squares) == 0
    assert board._eval_tempo(squares, nm, nbk, nbm, nwk, nwm) == 0
    assert board._eval_player_opposition(squares, nwm, nwk, nbk, nbm, nm, nk) == 0
    assert board.utility(WHITE) == -2


def test_successor_func_for_black():
    game = checkers.Checkers()
    board = game.curr_state

    # Tests whether initial game moves are correct from
    # Black's perspective
    moves = [m for m, _ in game.successors(board)]
    assert moves[0].affected_squares == [[17, BLACK | MAN, FREE], [23, FREE, BLACK | MAN]]
    assert moves[1].affected_squares == [[18, BLACK | MAN, FREE], [23, FREE, BLACK | MAN]]
    assert moves[2].affected_squares == [[18, BLACK | MAN, FREE], [24, FREE, BLACK | MAN]]
    assert moves[3].affected_squares == [[19, BLACK | MAN, FREE], [24, FREE, BLACK | MAN]]
    assert moves[4].affected_squares == [[19, BLACK | MAN, FREE], [25, FREE, BLACK | MAN]]
    assert moves[5].affected_squares == [[20, BLACK | MAN, FREE], [25, FREE, BLACK | MAN]]
    assert moves[6].affected_squares == [[20, BLACK | MAN, FREE], [26, FREE, BLACK | MAN]]


def test_successor_func_for_white():
    game = checkers.Checkers()
    board = game.curr_state
    # I'm cheating here ... white never moves first in
    # a real game, but I want to see that the moves
    # would work anyway.
    board.to_move = WHITE

    # Tests whether initial game moves are correct from
    # White's perspective
    moves = [m for m, _ in game.successors(board)]
    assert moves[0].affected_squares == [[34, WHITE | MAN, FREE], [29, FREE, WHITE | MAN]]
    assert moves[1].affected_squares == [[34, WHITE | MAN, FREE], [28, FREE, WHITE | MAN]]
    assert moves[2].affected_squares == [[35, WHITE | MAN, FREE], [30, FREE, WHITE | MAN]]
    assert moves[3].affected_squares == [[35, WHITE | MAN, FREE], [29, FREE, WHITE | MAN]]
    assert moves[4].affected_squares == [[36, WHITE | MAN, FREE], [31, FREE, WHITE | MAN]]
    assert moves[5].affected_squares == [[36, WHITE | MAN, FREE], [30, FREE, WHITE | MAN]]
    assert moves[6].affected_squares == [[37, WHITE | MAN, FREE], [31, FREE, WHITE | MAN]]


def test_black_new_king_can_move_backwards_out_of_king_row():
    """
    Regression test: after crowning, the piece is a KING and can move backwards
    (out of the king row) on its next turn.

    This checks king movement generation (KING_IDX) after a crowning move.
    """
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()

    # Crown a black man by a simple move.
    # You already have the baseline crowning move test for BLACK at 39->45.
    squares[39] = BLACK | MAN

    moves = game.legal_moves(board)
    assert len(moves) == 1
    crown_move = moves[0]
    assert crown_move.affected_squares == [
        [39, BLACK | MAN, FREE],
        [45, FREE, BLACK | KING],
    ]

    # Apply the move. make_move flips to_move, so force BLACK again to test king mobility.
    board.make_move(crown_move, notify=False, undo=False)
    board.to_move = BLACK

    moves_after = game.legal_moves(board)

    # The newly crowned king on 45 should be able to move "backwards" to 39.
    assert any(
        m.affected_squares
        == [
            [45, BLACK | KING, FREE],
            [39, FREE, BLACK | KING],
        ]
        for m in moves_after
    )


def test_white_new_king_can_move_backwards_out_of_king_row():
    """
    Same as above but for WHITE crowning on 15->9, then moving "backwards" to 15.
    """
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()

    squares[15] = WHITE | MAN

    moves = game.legal_moves(board)
    assert len(moves) == 1
    crown_move = moves[0]
    assert crown_move.affected_squares == [
        [15, WHITE | MAN, FREE],
        [9, FREE, WHITE | KING],
    ]

    board.make_move(crown_move, notify=False, undo=False)
    board.to_move = WHITE

    moves_after = game.legal_moves(board)

    # Newly crowned white king on 9 should be able to move "backwards" to 15.
    assert any(
        m.affected_squares
        == [
            [9, WHITE | KING, FREE],
            [15, FREE, WHITE | KING],
        ]
        for m in moves_after
    )


def test_forced_capture_suppresses_quiet_moves_black():
    """
    If any capture exists, legal_moves() must return captures only (forced capture rule).
    This relies on Checkers.legal_moves returning state.captures or state.moves.
    """
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()

    # Black man that has BOTH:
    # - a capture (6x12->18)
    # - and (typically) some quiet moves elsewhere (we add one on 7).
    squares[6] = BLACK | MAN
    squares[12] = WHITE | MAN  # enables capture to 18
    squares[7] = BLACK | MAN  # would have a quiet move if captures weren't forced

    moves = game.legal_moves(board)

    # All returned moves should be captures; simplest check: at least one move includes removing [12, WHITE|MAN, FREE].
    assert any([12, WHITE | MAN, FREE] in m.affected_squares for m in moves)

    # And no returned move should be a pure 2-square quiet move (your quiet moves are length 2).
    assert all(len(m.affected_squares) != 2 for m in moves)


def test_perft_depth0_is_1():
    game = checkers.Checkers()
    assert game.perft(0) == 1


def test_perft_depth1_equals_number_of_legal_moves_simple_position():
    """
    Perft(1) should always equal len(legal_moves(position)).
    This gives you a Perft regression test without needing any external reference counts.
    """
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()

    # A small, non-trivial position with a forced capture:
    squares[6] = BLACK | MAN
    squares[12] = WHITE | MAN

    moves = game.legal_moves(board)
    assert game.perft(1, board) == len(moves)


def test_perft_depth1_equals_number_of_legal_moves_multijump_position():
    """
    Same invariant as above, but on a multi-jump position (your movegen returns
    whole multi-jumps as a single Move via affected_squares).
    """
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()

    # This is essentially your existing "double jump" scenario:
    squares[41] = WHITE | MAN
    squares[36] = BLACK | MAN
    squares[25] = BLACK | MAN

    moves = game.legal_moves(board)
    assert game.perft(1, board) == len(moves)


import game.checkers as checkers
from util.globalconst import BLACK, WHITE, MAN, KING, FREE


def test_double_corner_block_white_wins_black_has_no_moves():
    """
    Double-corner block (white wins): Black to move is completely blocked.
    (This is essentially your commented-out Pask/SOIC Diagram state.)
    """
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = BLACK
    squares = board.squares
    board.clear()

    #   (white)
    #            45  46  47  48
    #          39  40  41  42
    #            34  35  36  37
    #          28  29  30  31
    #            23  24  25  26
    #          17  18  19  20
    #            12  13  14  15
    #          6   7   8   9
    #   (black)

    squares[35] = WHITE | KING
    squares[40] = WHITE | MAN
    squares[39] = BLACK | MAN
    squares[45] = BLACK | KING

    assert game.legal_moves(board) == []
    assert game.terminal_test(board) is True


def test_double_corner_block_black_wins_white_has_no_moves():
    """
    Double-corner block (black wins): White to move is completely blocked
    in black's double corner (square 9 in this indexing scheme).
    """
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()

    # White king trapped in the double corner at 9.
    # Exits from 9 are (typically) to 14 and 15.
    # - 14 is occupied by WHITE (so king cannot move there)
    # - 15 is occupied by BLACK, but the jump landing square off-board is not FREE,
    #   so no capture is available.
    # Also ensure the WHITE man on 14 has no legal moves.
    squares[9] = WHITE | KING
    squares[14] = WHITE | MAN  # blocks one king exit
    squares[15] = BLACK | MAN  # blocks other king exit
    squares[20] = BLACK | KING  # prevents king from capturing through 15 (landing isn't FREE)
    squares[8] = BLACK | MAN  # blocks the white man on 14 from moving to 8

    assert game.legal_moves(board) == []
    assert game.terminal_test(board) is True


def test_single_corner_block_white_wins_black_has_no_moves():
    """
    Single-corner block (white wins): Black to move is blocked in white's single corner (48).
    Corner 48 has only one adjacent playable square (typically 42).
    """
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = BLACK
    squares = board.squares
    board.clear()

    # Black king trapped in the single corner at 48.
    squares[48] = BLACK | KING
    squares[42] = BLACK | MAN  # blocks the king's only exit
    squares[47] = WHITE | MAN  # blocks the man at 42 from moving (prevents 42->47)

    assert game.legal_moves(board) == []
    assert game.terminal_test(board) is True


def test_single_corner_block_black_wins_white_has_no_moves():
    """
    Single-corner block (black wins): White to move is blocked in black's single corner (6).
    Corner 6 has only one adjacent playable square (typically 12).
    """
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()

    # White king trapped in the single corner at 6.
    squares[6] = WHITE | KING
    squares[12] = WHITE | MAN  # blocks the king's only exit
    squares[7] = BLACK | MAN  # blocks the man at 12 from moving (prevents 12->7)

    assert game.legal_moves(board) == []
    assert game.terminal_test(board) is True
