__author__ = 'brandon_corfman'
import multiprocessing
from abc import ABCMeta, abstractmethod
from goal import Goal
from utils import argmin_score
from formation import BLACK_MAP
from globalconst import FIRST, LAST, ACTIVE, INACTIVE, COMPLETED


def get_score_move(board):
    def score_move(move):
        player = board.to_move
        board.make_move(move, False, False)
        score = board.utility(player)
        board.undo_move(move, False, False)
        return score
    return score_move


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


def generate_common_domain(formation):
    domain = set()
    for pos in formation:
        domain = domain.union(BLACK_MAP[pos])
    return domain


def calc_best_move(formation, owner, term_event, child_conn):
    term_event.clear()
    board = owner.board
    game = owner.game
    primary, secondary = partition_moves(game.legal_moves(), generate_common_domain(formation))
    if not primary and not secondary:
        print primary
        print secondary
        print "Error"
        child_conn.send(None)
        return

    score_func = get_score_move(board)
    primary_move, primary_score = None, 999
    if primary:
        primary_move, primary_score = argmin_score(primary, score_func)
        primary_score -= 1  # bonus for primary moves since they are within the formation
    secondary_move, secondary_score = None, 0
    if secondary:
        secondary_move, secondary_score = argmin_score(secondary, score_func)
    if term_event.is_set():  # a signal means terminate
        term_event.clear()
        child_conn.send(None)
        return
    move = primary_move if primary_score <= secondary_score else secondary_move
    child_conn.send(move)


class GoalFormation(Goal):
    __metaclass__ = ABCMeta

    def __init__(self, owner):
        Goal.__init__(self, owner)
        self.child_conn = owner.controller.child_conn
        self._term_event = multiprocessing.Event()
        self._process = None

    def activate(self):
        self.status = ACTIVE

    @abstractmethod
    def process(self):
        pass

    def terminate(self):
        self.status = INACTIVE


class GoalShortDyke(GoalFormation):
    def __init__(self, owner):
        GoalFormation.__init__(self, owner)

    def __repr__(self):
        return "GoalShortDyke"

    def process(self):
        self.activate_if_inactive()
        self._process = multiprocessing.Process(target=calc_best_move,
                                                args=(self.owner.board.short_dyke,
                                                      self.owner,
                                                      self._term_event,
                                                      self.child_conn))
        self._process.daemon = True
        self._process.start()
        return COMPLETED


class GoalLongDyke(GoalFormation):
    def __init__(self, owner):
        GoalFormation.__init__(self, owner)

    def __repr__(self):
        return "GoalLongDyke"

    def process(self):
        self.activate_if_inactive()
        self._process = multiprocessing.Process(target=calc_best_move,
                                                args=(self.owner.board.long_dyke,
                                                      self.owner,
                                                      self._term_event,
                                                      self.child_conn))
        self._process.daemon = True
        self._process.start()
        return ACTIVE


class GoalPyramid(GoalFormation):
    def __init__(self, owner):
        GoalFormation.__init__(self, owner)

    def __repr__(self):
        return "GoalPyramid"

    def process(self):
        self.activate_if_inactive()
        self._process = multiprocessing.Process(target=calc_best_move,
                                                args=(self.owner.board.pyramid,
                                                      self.owner,
                                                      self._term_event,
                                                      self.child_conn))
        self._process.daemon = True
        self._process.start()
        return ACTIVE

class GoalPhalanx(GoalFormation):
    def __init__(self, owner):
        GoalFormation.__init__(self, owner)

    def __repr__(self):
        return "GoalPhalanx"

    def process(self):
        self.activate_if_inactive()
        self._process = multiprocessing.Process(target=calc_best_move,
                                                args=(self.owner.board.phalanx,
                                                      self.owner,
                                                      self._term_event,
                                                      self.child_conn))
        self._process.daemon = True
        self._process.start()


class GoalMill(GoalFormation):
    def __init__(self, owner):
        GoalFormation.__init__(self, owner)

    def __repr__(self):
        return "GoalMill"

    def process(self):
        self.activate_if_inactive()
        self._process = multiprocessing.Process(target=calc_best_move,
                                                args=(self.owner.board.mill,
                                                      self.owner,
                                                      self._term_event,
                                                      self.child_conn))
        self._process.daemon = True
        self._process.start()


class GoalEchelon(GoalFormation):
    def __init__(self, owner):
        GoalFormation.__init__(self, owner)

    def __repr__(self):
        return "GoalEchelon"

    def process(self):
        self.activate_if_inactive()
        self._process = multiprocessing.Process(target=calc_best_move,
                                                args=(self.owner.board.echelon,
                                                      self.owner,
                                                      self._term_event,
                                                      self.child_conn))
        self._process.daemon = True
        self._process.start()
