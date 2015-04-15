from abc import ABCMeta, abstractmethod
from formation import BLACK_MAP
from globalconst import FIRST, LAST
from utils import argmax_score


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


class Goal:
    __metaclass__ = ABCMeta

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3

    def __init__(self, owner):
        self.owner = owner
        self.status = self.INACTIVE

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def terminate(self):
        pass

    def handle_message(self, msg):
        return False

    def reactivate_if_failed(self):
        if self.status == self.FAILED:
            self.status = self.INACTIVE

    def activate_if_inactive(self):
        if self.status == self.INACTIVE:
            self.status = self.ACTIVE

    def is_complete(self):
        return self.status == self.COMPLETED

    def has_failed(self):
        return self.status == self.FAILED

    def is_active(self):
        return self.status == self.ACTIVE

    def make_best_move(self, formation):
        board = self.owner.board
        game = self.owner.game
        primary, secondary = partition_moves(game.legal_moves(), generate_common_domain(formation))
        if not primary and not secondary:
            self.status = self.FAILED
            return

        score_func = get_score_move(board)
        primary_move, primary_score = argmax_score(primary, score_func)
        primary_score += 3  # bonus for primary moves since they are within the formation
        secondary_move, secondary_score = argmax_score(secondary, score_func)
        move = primary_move if primary_score >= secondary_score else secondary_move
        board.make_move(move)

