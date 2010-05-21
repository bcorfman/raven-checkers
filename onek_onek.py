from globalconst import BLACK, WHITE, MAN, KING
from goalevaluator import GoalEvaluator
from onekingattack import Goal_OneKingAttack

class OneKingAttackOneKingEvaluator(GoalEvaluator):
    def __init__(self, bias):
        GoalEvaluator.__init__(self, bias)

    def calculateDesirability(self, board):
        plr_color = board.to_move
        enemy_color = board.enemy
        # if we don't have one man on each side or the player
        # doesn't have the opposition, then goal is undesirable.
        if (board.count(BLACK) != 1 or board.count(WHITE) != 1 or
            not board.has_opposition(plr_color)):
            return 0.0
        player = board.get_pieces(plr_color)[0]
        p_idx, p_val = player
        p_row, p_col = board.row_col_for_index(p_idx)
        enemy = board.get_pieces(enemy_color)[0]
        e_idx, e_val = enemy
        e_row, e_col = board.row_col_for_index(e_idx)
        # must be two kings against each other and the distance
        # between them at least three rows away
        if ((p_val & KING) and (e_val & KING) and
            (abs(p_row - e_row) > 2 or abs(p_col - e_col) > 2)):
            return 1.0
        return 0.0

    def setGoal(self, board):
        player = board.to_move
        board.removeAllSubgoals()
        if player == WHITE:
            goalset = board.addWhiteSubgoal
        else:
            goalset = board.addBlackSubgoal
        goalset(Goal_OneKingAttack())

class OneKingFleeOneKingEvaluator(GoalEvaluator):
    def __init__(self, bias):
        GoalEvaluator.__init__(self, bias)

    def calculateDesirability(self, board):
        plr_color = board.to_move
        enemy_color = board.enemy
        # if we don't have one man on each side or the player
        # has the opposition (meaning we should attack instead),
        # then goal is not applicable.
        if (board.count(BLACK) != 1 or board.count(WHITE) != 1 or
            board.has_opposition(plr_color)):
            return 0.0
        player = board.get_pieces(plr_color)[0]
        p_idx, p_val = player
        enemy = board.get_pieces(enemy_color)[0]
        e_idx, e_val = enemy
        # must be two kings against each other; otherwise it's
        # not applicable.
        if not ((p_val & KING) and (e_val & KING)):
            return 0.0
        return 1.0

    def setGoal(self, board):
        player = board.to_move
        board.removeAllSubgoals()
        if player == WHITE:
            goalset = board.addWhiteSubgoal
        else:
            goalset = board.addBlackSubgoal
        goalset(Goal_OneKingFlee(board))
