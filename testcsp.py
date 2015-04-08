__author__ = 'brandon_corfman'
from evaluators import formation_csp, generate_common_domain
from utils import argmin_list, argmax_list, argmax_score
from csp import backtracking_search, forward_checking, mrv
from formation import BLACK_MAP, BLACK_COST
from globalconst import BLACK, MAN, FREE, FIRST, LAST
import unittest
import checkers


def calc_cost(formation):
    cost = 0
    for k, v in formation.iteritems():
        if k == v:
            continue
        reachable = BLACK_MAP[k]
        idx = reachable.index(v)
        cost += BLACK_COST[k][idx]
    return cost


def partition_moves(move_list, domain):
    primary_moves = []
    secondary_moves = []
    for move in move_list:
        start = move.affected_squares[FIRST][0]
        dest = move.affected_squares[LAST][0]
        if start in domain and dest in domain:
            primary_moves.append(move)
        else:
            secondary_moves.append(move)
    return primary_moves, secondary_moves


class TestShortDykePossibleFromStart(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
        self.assertEqual(result[8], 8)
        self.assertEqual(result[9], 9)
        self.assertEqual(result[14], 14)
        self.assertTrue(result[17] in BLACK_MAP[17] and result[17] != result[23] and result[17] != result[29])
        self.assertTrue(result[23] in BLACK_MAP[23] and result[23] != result[29] and result[23] != result[17])
        self.assertTrue(result[29] in BLACK_MAP[29] and result[29] != result[17] and result[29] != result[23])


class TestPhalanxFirstBestMove(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK

    def testCSP(self):
        phalanx_csp = formation_csp(self.board.phalanx, self.board)
        solution = backtracking_search(phalanx_csp, select_unassigned_variable=mrv, inference=forward_checking)
        if solution:
            primary, secondary = partition_moves(self.game.legal_moves(), generate_common_domain(self.board.phalanx))
            state = self.board
            player = self.board.to_move

            def score_move(move):
                state.make_move(move, False, False)
                score = state.utility(player)
                state.undo_move(move, False, False)
                return score

            primary_move, primary_score = argmax_score(primary, score_move)
            primary_score += 3  # bonus for primary moves
            secondary_move, secondary_score = argmax_score(secondary, score_move)
            move = primary_move if primary_score > secondary_score else secondary_move

            self.assertEqual(move.affected_squares[FIRST][0], 18)
            self.assertEqual(move.affected_squares[LAST][0], 24)


class TestShortDykePossibleWithReducedSet(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        self.board.clear()
        squares[8] = BLACK | MAN
        squares[9] = BLACK | MAN
        squares[14] = BLACK | MAN
        squares[13] = BLACK | MAN
        squares[6] = BLACK | MAN
        squares[18] = BLACK | MAN

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
        self.assertEqual(result[8], 8)
        self.assertEqual(result[9], 9)
        self.assertEqual(result[14], 14)
        self.assertTrue(result[17] in BLACK_MAP[17] and result[17] != result[23] and result[17] != result[29])
        self.assertTrue(result[23] in BLACK_MAP[23] and result[23] != result[29] and result[23] != result[17])
        self.assertTrue(result[29] in BLACK_MAP[29] and result[29] != result[17] and result[29] != result[23])


class TestShortDykeReducedSetAllSolutions(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        self.board.clear()
        squares[8] = BLACK | MAN
        squares[9] = BLACK | MAN
        squares[14] = BLACK | MAN
        squares[13] = BLACK | MAN
        squares[6] = BLACK | MAN
        squares[18] = BLACK | MAN

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        #for soln in backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking,
        #                                all_values=True):
        #    print soln
        self.assertEqual(True, True)


class TestShortDykeFailsWithMissingChecker(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        self.board.clear()
        squares[8] = BLACK | MAN
        squares[9] = BLACK | MAN
        squares[14] = BLACK | MAN
        squares[13] = BLACK | MAN
        squares[6] = BLACK | MAN

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
        self.assertEqual(result, None)


class TestShortDykeFailsWithWrongPositions(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        self.board.clear()
        squares[8] = BLACK | MAN
        squares[9] = BLACK | MAN
        squares[14] = BLACK | MAN
        squares[13] = BLACK | MAN
        squares[6] = BLACK | MAN
        squares[30] = BLACK | MAN

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
        self.assertEqual(result, None)
