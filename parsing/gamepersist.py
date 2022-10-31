import copy
from util.globalconst import FIRST, KING_IDX, LAST, square_map
from game.checkers import Checkers, Checkerboard
from base.move import Move


class SavedGame(object):
    def __init__(self):
        self._model = Checkers()
        self.to_move = None
        self.moves = []
        self.description = ''
        self.black_men = []
        self.white_men = []
        self.black_kings = []
        self.white_kings = []
        self.flip_board = False
        self.num_players = 1
        self._bm_check = False
        self._bk_check = False
        self._wm_check = False
        self._wk_check = False

    def _is_move(self, delta):
        return delta in KING_IDX

    def _try_move(self, move: Move, state_copy: Checkerboard):
        legal_moves = self._model.legal_moves(state_copy)
        # match move from file with available moves on checkerboard
        found = False
        start, dest = move.affected_squares[FIRST], move.affected_squares[LAST]
        for move in legal_moves:
            if start == move.affected_squares[FIRST] and dest == move.affected_squares[LAST]:
                self._model.make_move(move, state_copy, False, False)
                self.moves.append(move)
                found = True
                break
        if not found:
            raise RuntimeError(f"Illegal move {move} found")

    def _try_jump(self, pdn_move: Move, state_copy: Checkerboard):
        if not self._model.captures_available(state_copy):
            return False
        legal_moves = self._model.legal_moves(state_copy)
        # PDN move follows format [first, mid1, mid2, ..., last]
        found = False
        valid_moves = []
        for mv in legal_moves:
            # a valid jump may either have a single jump in it, or
            # multiple jumps. In the multiple jump case, start_square is the
            # source of the first jump, and dest_square is the endpoint of the
            # last jump.
            for sq in mv.affected_squares:
                if start == mv.affected_squares[FIRST][0] and dest == mv.affected_squares[LAST]:
                    self._model.make_move(mv, state_copy, False, False)
                    valid_moves.append(mv)
                    found = True
                    break
        return found

    def _translate_moves_to_board(self, moves: list[Move]):
        """ Each move in the file lists the beginning and ending square, along
        with an optional annotation string (in Creole fmt) that describes it.
        I make sure that each move works on a copy of the model before I commit
        to using it inside the code. """
        state_copy = copy.deepcopy(self._model.curr_state)

        # analyze affected squares to perform a move or jump.
        idx = 0
        moves_len = len(moves)
        while idx < moves_len:
            delta = abs(moves[idx].affected_squares[0] - moves[idx].affected_squares[1])
            if self._is_move(delta):
                self._try_move(moves[idx], state_copy)
            else:
                jumped = self._try_jump(moves[idx], state_copy)
                if not jumped:
                    raise RuntimeError(f"Bad move at index {idx}")
        moves.reverse()  # TODO: is this still needed?
        return moves
