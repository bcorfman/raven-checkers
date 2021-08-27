import sys
from goal import Goal
from composite import CompositeGoal

class Goal_OneKingFlee(CompositeGoal):
    def __init__(self, owner):
        CompositeGoal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE
        self.removeAllSubgoals()
        # because goals are *pushed* onto the front of the subgoal list they must
        # be added in reverse order.
        self.addSubgoal(Goal_MoveTowardNearestDoubleCorner(self.owner))
        self.addSubgoal(Goal_SeeSaw(self.owner))

    def process(self):
        self.activateIfInactive()
        return self.processSubgoals()

    def terminate(self):
        self.status = self.INACTIVE

class Goal_MoveTowardBestDoubleCorner(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)
        self.dc = [8, 13, 27, 32]

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
        
        # pick DC that isn't blocked by enemy
        lowest_dist = sys.maxint
        dc = 0 
        for i in self.dc:
            dc_row, dc_col = self.owner.row_col_for_index(i)
            pdist = abs(dc_row - p_row) + abs(dc_col - p_col)
            edist = abs(dc_row - e_row) + abs(dc_col - e_col)
            if pdist < lowest_dist and edist > pdist:
                lowest_dist = pdist
                dc = i
                
        # if lowest distance is 0, then goal is complete.
        if lowest_dist == 0:
            self.status = self.COMPLETED
            return
        
        # select the available move that decreases the distance
        # between the original player position and the chosen double corner.
        # If no such move exists, the goal has failed.
        dc_row, dc_col = self.owner.row_col_for_index(dc)
        good_move = None
        for m in self.owner.moves:
            # try a move and gather the new row & col for the player
            self.owner.make_move(m, False, False)
            plr_update = self.owner.get_pieces(plr_color)[0]
            pu_idx, _ = plr_update
            pu_row, pu_col = self.owner.row_col_for_index(pu_idx)
            self.owner.undo_move(m, False, False)
            new_diff = abs(pu_row - dc_row) + abs(pu_col - dc_col)
            if new_diff < lowest_dist:
                good_move = m
                break
        if good_move:
            self.owner.make_move(good_move, True, True)
        else:
            self.status = self.FAILED
        
    def terminate(self):
        self.status = self.INACTIVE
    
class Goal_SeeSaw(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # for now, I'm not even sure I need this goal, but I'm saving it
        # as a placeholder.
        self.status = self.COMPLETED

    def terminate(self):
        self.status = self.INACTIVE
    