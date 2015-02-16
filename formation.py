__author__ = 'brandon_corfman'
from csp import CSP, different_values_constraint, backtracking_search
from globalconst import BLACK_MAP, WHITE_MAP, BLACK, WHITE, MAN


def formation_csp(formation, board):
    """Return an instance of the CSP to see if the formation can be obtained on the board."""
    domains = {}
    player = board.to_move
    pos_map = BLACK_MAP if player == BLACK else WHITE_MAP
    neighbors = {}
    for f in formation:
        domains[f] = [pos for pos in pos_map[f] if board.squares[pos] == player + MAN]
        neighbors[f] = set(formation) - {f}
    return CSP(formation, domains, neighbors, different_values_constraint)

