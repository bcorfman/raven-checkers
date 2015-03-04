__author__ = 'brandon_corfman'
from goal import Goal
from formation import measure_formation_closeness


def select_best_move_to_achieve_formation(formation, board):
    orig_score = measure_formation_closeness(formation, board)
    if orig_score == 0:
        return False
    legal_moves = board.captures or board.moves
    best_move = None
    for move in legal_moves:
        board.make_move(move, False, False)
        move_score = measure_formation_closeness(formation, board)
        if 0 < move_score < orig_score and not board.captures:
            best_move = move
        board.undo_move(move, False, False)
    if not best_move:
        return False
    else:
        board.make_move(best_move, True, True)
        return True


class GoalShortDyke(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        board = self._thinker.model
        if not select_best_move_to_achieve_formation(board.short_dyke, board):
            self.status = self.FAILED

    def terminate(self):
        self.status = self.INACTIVE


class GoalLongDyke(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        board = self._thinker.model
        if not select_best_move_to_achieve_formation(board.long_dyke, board):
            self.status = self.FAILED

    def terminate(self):
        self.status = self.INACTIVE


class GoalPyramid(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        board = self._thinker.model
        if not select_best_move_to_achieve_formation(board.pyramid, board):
            self.status = self.FAILED

    def terminate(self):
        self.status = self.INACTIVE


class GoalPhalanx(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        board = self._thinker.model
        if not select_best_move_to_achieve_formation(board.phalanx, board):
            self.status = self.FAILED

    def terminate(self):
        self.status = self.INACTIVE


class GoalMill(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        board = self._thinker.model
        if not select_best_move_to_achieve_formation(board.mill, board):
            self.status = self.FAILED

    def terminate(self):
        self.status = self.INACTIVE


class GoalEchelon(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        board = self._thinker.model
        if not select_best_move_to_achieve_formation(board.echelon, board):
            self.status = self.FAILED

    def terminate(self):
        self.status = self.INACTIVE
