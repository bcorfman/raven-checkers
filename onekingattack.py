from goal import Goal
from composite import CompositeGoal

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

    def terminate(self):
        self.status = self.INACTIVE

class Goal_MoveTowardEnemy(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activateIfInactive()
        
        # only moves (not captures) are a valid goal
        if self.owner.captures:
            self.status = self.FAILED
            return
        
        # identify player king and enemy king
        plr_color = self.owner.to_move
        enemy_color = self.owner.enemy
        player = self.owner.get_pieces(plr_color)[0]
        p_idx, _ = player
        p_row, p_col = self.owner.row_col_for_index(p_idx)
        enemy = self.owner.get_pieces(enemy_color)[0]
        e_idx, _ = enemy
        e_row, e_col = self.owner.row_col_for_index(e_idx)
        
        # if distance between player and enemy is already down
        # to 2 rows or cols, then goal is complete.
        if abs(p_row - e_row) == 2 or abs(p_col - e_col) == 2:
            self.status = self.COMPLETED
            
        # select the available move that decreases the distance
        # between the player and the enemy. If no such move exists, 
        # the goal has failed.
        good_move = None
        for m in self.owner.moves:
            # try a move and gather the new row & col for the player
            self.owner.make_move(m, False, False)
            plr_update = self.owner.get_pieces(plr_color)[0]
            pu_idx, _ = plr_update
            pu_row, pu_col = self.owner.row_col_for_index(pu_idx)
            self.owner.undo_move(m, False, False)
            new_diff = abs(pu_row - e_row) + abs(pu_col - e_col)
            old_diff = abs(p_row - e_row) + abs(p_col - e_col)
            if new_diff < old_diff:
                good_move = m
                break
        if good_move:
            self.owner.make_move(good_move, True, True)
        else:
            self.status = self.FAILED
        
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
