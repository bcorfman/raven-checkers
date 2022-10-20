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
    assert moves[0].affected_squares == [[6, BLACK | MAN, FREE],
                                         [12, WHITE | MAN, FREE],
                                         [18, FREE, BLACK | MAN]]


def test_black_man_double_jump():
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    squares[6] = BLACK | MAN
    squares[12] = WHITE | MAN
    squares[23] = WHITE | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[6, BLACK | MAN, FREE],
                                         [12, WHITE | MAN, FREE],
                                         [18, FREE, FREE],
                                         [23, WHITE | MAN, FREE],
                                         [28, FREE, BLACK | MAN]]


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
    assert moves[0].affected_squares == [[12, BLACK | MAN, FREE],
                                         [18, WHITE | MAN, FREE],
                                         [24, FREE, FREE],
                                         [30, WHITE | MAN, FREE],
                                         [36, FREE, FREE],
                                         [41, WHITE | MAN, FREE],
                                         [46, FREE, BLACK | KING]]


def test_black_man_crown_king_on_move():
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    squares[39] = BLACK | MAN
    squares[18] = WHITE | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[39, BLACK | MAN, FREE],
                                         [45, FREE, BLACK | KING]]


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
    assert moves[0].affected_squares == [[13, BLACK | KING, FREE],
                                         [18, WHITE | MAN, FREE],
                                         [23, FREE, FREE],
                                         [29, WHITE | MAN, FREE],
                                         [35, FREE, FREE],
                                         [30, WHITE | MAN, FREE],
                                         [25, FREE, FREE],
                                         [19, WHITE | MAN, FREE],
                                         [13, FREE, BLACK | KING]]
    assert moves[1].affected_squares == [[13, BLACK | KING, FREE],
                                         [19, WHITE | MAN, FREE],
                                         [25, FREE, FREE],
                                         [30, WHITE | MAN, FREE],
                                         [35, FREE, FREE],
                                         [29, WHITE | MAN, FREE],
                                         [23, FREE, FREE],
                                         [18, WHITE | MAN, FREE],
                                         [13, FREE, BLACK | KING]]


def test_white_man_single_jump():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()
    squares[41] = WHITE | MAN
    squares[36] = BLACK | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[41, WHITE | MAN, FREE],
                                         [36, BLACK | MAN, FREE],
                                         [31, FREE, WHITE | MAN]]


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
    assert moves[0].affected_squares == [[41, WHITE | MAN, FREE],
                                         [36, BLACK | MAN, FREE],
                                         [31, FREE, FREE],
                                         [25, BLACK | MAN, FREE],
                                         [19, FREE, WHITE | MAN]]


def test_white_man_crown_king_on_move():
    game = checkers.Checkers()
    board = game.curr_state
    board.to_move = WHITE
    squares = board.squares
    board.clear()
    squares[15] = WHITE | MAN
    squares[36] = BLACK | MAN
    moves = game.legal_moves(board)
    assert moves[0].affected_squares == [[15, WHITE | MAN, FREE],
                                         [9, FREE, WHITE | KING]]


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
    assert moves[0].affected_squares == [[41, WHITE | MAN, FREE],
                                         [36, BLACK | MAN, FREE],
                                         [31, FREE, FREE],
                                         [25, BLACK | MAN, FREE],
                                         [19, FREE, FREE],
                                         [13, BLACK | KING, FREE],
                                         [7, FREE, WHITE | KING]]


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
    assert moves[0].affected_squares == [[13, WHITE | KING, FREE],
                                         [18, BLACK | MAN, FREE],
                                         [23, FREE, FREE],
                                         [29, BLACK | MAN, FREE],
                                         [35, FREE, FREE],
                                         [30, BLACK | MAN, FREE],
                                         [25, FREE, FREE],
                                         [19, BLACK | MAN, FREE],
                                         [13, FREE, WHITE | KING]]
    assert moves[1].affected_squares == [[13, WHITE | KING, FREE],
                                         [19, BLACK | MAN, FREE],
                                         [25, FREE, FREE],
                                         [30, BLACK | MAN, FREE],
                                         [35, FREE, FREE],
                                         [29, BLACK | MAN, FREE],
                                         [23, FREE, FREE],
                                         [18, BLACK | MAN, FREE],
                                         [13, FREE, WHITE | KING]]


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
    assert board._eval_player_opposition(squares, nwm, nwk, nbk,
                                         nbm, nm, nk) == 0
    assert board.utility(WHITE) == -2


def test_successor_func_for_black():
    game = checkers.Checkers()
    board = game.curr_state

    # Tests whether initial game moves are correct from
    # Black's perspective
    moves = [m for m, _ in game.successors(board)]
    assert moves[0].affected_squares == [[17, BLACK | MAN, FREE],
                                         [23, FREE, BLACK | MAN]]
    assert moves[1].affected_squares == [[18, BLACK | MAN, FREE],
                                         [23, FREE, BLACK | MAN]]
    assert moves[2].affected_squares == [[18, BLACK | MAN, FREE],
                                         [24, FREE, BLACK | MAN]]
    assert moves[3].affected_squares == [[19, BLACK | MAN, FREE],
                                         [24, FREE, BLACK | MAN]]
    assert moves[4].affected_squares == [[19, BLACK | MAN, FREE],
                                         [25, FREE, BLACK | MAN]]
    assert moves[5].affected_squares == [[20, BLACK | MAN, FREE],
                                         [25, FREE, BLACK | MAN]]
    assert moves[6].affected_squares == [[20, BLACK | MAN, FREE],
                                         [26, FREE, BLACK | MAN]]


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
    assert moves[0].affected_squares == [[34, WHITE | MAN, FREE],
                                         [29, FREE, WHITE | MAN]]
    assert moves[1].affected_squares == [[34, WHITE | MAN, FREE],
                                         [28, FREE, WHITE | MAN]]
    assert moves[2].affected_squares == [[35, WHITE | MAN, FREE],
                                         [30, FREE, WHITE | MAN]]
    assert moves[3].affected_squares == [[35, WHITE | MAN, FREE],
                                         [29, FREE, WHITE | MAN]]
    assert moves[4].affected_squares == [[36, WHITE | MAN, FREE],
                                         [31, FREE, WHITE | MAN]]
    assert moves[5].affected_squares == [[36, WHITE | MAN, FREE],
                                         [30, FREE, WHITE | MAN]]
    assert moves[6].affected_squares == [[37, WHITE | MAN, FREE],
                                         [31, FREE, WHITE | MAN]]
