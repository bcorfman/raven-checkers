from globalconst import *

class Action(object):
    def __init__(self):
        self.player = state.to_move
        self.player_total = state.white_total if player == WHITE else state.black_total
        self.enemy = BLACK if state.to_move == WHITE else WHITE
        self.enemy_total = state.white_total if enemy == WHITE else state.black_total
        self.plr_lst = state.get_pieces(player)
        self.enemy_lst = state.get_pieces(enemy)

    def precondition(self, state, **params):
        raise NotImplementedError()

    def postcondition(self, state, **params):
        raise NotImplementedError()

class PinEnemyKingInCornerWithPlayerKing(Action):
    def __init__(self):
        Action.__init__(self)
        self.pidx = 0
        self.eidx = 0
        self.goal = 8

    def precondition(self, state):
        self.pidx, plr = self.plr_lst[0]      # only 1 piece per side
        self.eidx, enemy = self.enemy_lst[0]
        delta = abs(self.pidx - self.eidx)
        return ((self.player_total == 1) and (self.enemy_total == 1) and
                (plr & KING > 0) and (enemy & KING > 0) and
                not (8 <= delta <= 10) and state.have_opposition(player))

    def postcondition(self, state):
        new_state = None
        old_delta = abs(self.eidx - self.pidx)
        goal_delta = abs(self.goal - old_delta)
        for move in state.moves:
            for m in move:
                newidx, _, _ = m[1]
                new_delta = abs(self.eidx - newidx)
                if abs(goal - new_delta) < goal_delta:
                    new_state = state.make_move(move)
                    break
        return new_state

#   (white)
#            37  38  39  40
#          32  33  34  35
#            28  29  30  31
#          23  24  25  26
#            19  20  21  22
#          14  15  16  17
#            10  11  12  13
#          5   6   7   8
#   (black)

class SingleKingFleeToDoubleCorner(Action):
    def __init__(self):
        Action.__init__(self)
        self.pidx = 0
        self.eidx = 0
        self.dest = [8, 13, 27, 32]
        self.goal_delta = 0

    def precondition(self, state):
        # fail fast
        if self.player_total == 1 and self.enemy_total == 1:
            return False
        self.pidx, plr = self.plr_lst[0]
        self.eidx, enemy = self.enemy_lst[0]
        for sq in self.dest:
            if abs(self.pidx - sq) < abs(self.eidx - sq):
                self.goal = sq
                return True
        return False

    def postcondition(self, state):
        self.goal_delta = abs(self.goal - self.pidx)
        for move in state.moves:
            for m in move:
                newidx, _, _ = m[1]
                new_delta = abs(self.goal - newidx)
                if new_delta < goal_delta:
                    new_state = state.make_move(move)
                    break
        return new_state

class FormShortDyke(Action):
    def __init__(self):
        Action.__init__(self)
