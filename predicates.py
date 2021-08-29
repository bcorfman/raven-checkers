from globalconst import BLACK, WHITE, KING


class Operator(object):
    pass


class OneKingAttackOneKing(Operator):
    def precondition(self, board):
        plr_color = board.to_move
        opp_color = board.enemy
        return (board.count(plr_color) == 1 and board.count(opp_color) == 1 and
                any((x & KING for x in board.get_pieces(opp_color))) and
                any((x & KING for x in board.get_pieces(plr_color))) and
                board.has_opposition(plr_color))
    
    def postcondition(self, board):
        board.make_move()


class PinEnemyKingInCornerWithPlayerKing(Operator):
    def __init__(self):
        self.p_idx = 0
        self.e_idx = 0
        self.goal = 8

    def precondition(self, state):
        self.p_idx, plr = self.plr_lst[0]      # only 1 piece per side
        self.e_idx, enemy = self.enemy_lst[0]
        delta = abs(self.p_idx - self.e_idx)
        return ((self.player_total == 1) and (self.enemy_total == 1) and
                (plr & KING > 0) and (enemy & KING > 0) and
                not (8 <= delta <= 10) and state.have_opposition(plr))

    def postcondition(self, state):
        new_state = None
        old_delta = abs(self.e_idx - self.p_idx)
        goal_delta = abs(self.goal - old_delta)
        for move in state.moves:
            for m in move:
                newidx, _, _ = m[1]
                new_delta = abs(self.e_idx - newidx)
                if abs(self.goal - new_delta) < goal_delta:
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


class SingleKingFleeToDoubleCorner(Operator):
    def __init__(self):
        self.p_idx = 0
        self.e_idx = 0
        self.dest = [8, 13, 27, 32]
        self.goal_delta = 0

    def precondition(self, state):
        # fail fast
        if self.player_total == 1 and self.enemy_total == 1:
            return False
        self.p_idx, _ = self.plr_lst[0]
        self.e_idx, _ = self.enemy_lst[0]
        for sq in self.dest:
            if abs(self.p_idx - sq) < abs(self.e_idx - sq):
                self.goal = sq
                return True
        return False

    def postcondition(self, state):
        self.goal_delta = abs(self.goal - self.p_idx)
        new_state = None
        for move in state.moves:
            for m in move:
                new_idx, _, _ = m[1]
                new_delta = abs(self.goal - new_idx)
                if new_delta < self.goal_delta:
                    new_state = state.make_move(move)
                    break
        return new_state


class FormShortDyke(Operator):
    def precondition(self):
        pass
    