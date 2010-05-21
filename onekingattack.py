from goal import Goal

class Goal_OneKingAttack(CompositeGoal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE
        self.removeAllSubgoals()
        # because goals are *pushed* onto the front of the subgoal list they must
        # be added in reverse order.
        self.addSubgoal(Goal_MoveTowardEnemy(self.owner))
        self.addSubgoal(Goal_PinEnemy(self.owner))

    def process(self):
        self.activateIfInactive()
        return self.processSubgoals()


class Goal_MoveTowardEnemy(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activateIfInactive()

        if self.owner.captures:
        for m in self.owner.moves:
            for src, mid, dest in m:


        plr_color = self.owner.to_move
        enemy_color = self.owner.enemy
        player = self.owner.get_pieces(plr_color)[0]
        p_idx, _ = player
        p_row, p_col = self.owner.row_col_for_index(p_idx)
        enemy = self.owner.get_pieces(enemy_color)[0]
        e_idx, _ = enemy
        e_row, e_col = self.owner.row_col_for_index(e_idx)
        # must be two kings against each other and the distance
        # between them at least three rows away
        if ((p_val & KING) and (e_val & KING) and
            (abs(p_row - e_row) > 2 or abs(p_col - e_col) > 2)):
            return 1.0
    def terminate(self):
        self.status = self.INACTIVE

class Goal_PinEnemy(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        pass

    def terminate(self):
        self.status = self.INACTIVE
