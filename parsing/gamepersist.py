import copy
from util.globalconst import square_map
from game.checkers import Checkers, Checkerboard


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
        return delta in [4, 5]

    def _try_move(self, squares: list, annotation: str, state_copy: Checkerboard):
        legal_moves = self._model.legal_moves(state_copy)
        # try to match squares with available moves on checkerboard
        sq_len = len(squares)
        for move in legal_moves:
            if sq_len == len(move.affected_squares) and \
                    all(square_map[sq] == move.affected_squares[i][0] for i, sq in enumerate(squares)):
                move.annotation = annotation
                self._model.make_move(move, state_copy, False, False)
                self.moves.append(move)
                return True
        else:
            raise RuntimeError(f"Illegal move {squares} found")

    def _try_jump(self, squares: list, annotation: str, state_copy: Checkerboard):
        if not self._model.captures_available(state_copy):
            return False
        legal_moves = self._model.legal_moves(state_copy)
        found = False
        for move in legal_moves:
            if all(sq == move.affected_squares[i][0] for i, sq in enumerate(squares)):
                move.annotation = annotation
                self._model.make_move(move, state_copy, False, False)
                self.moves.append(move)
                found = True
                break
        return found

    def translate_moves_to_board(self, moves: list):
        """ Each move in the file lists the beginning and ending square, along
        with an optional annotation string (in Creole fmt) that describes it.
        I make sure that each move works on a copy of the model before I commit
        to using it inside the code. """
        state_copy = copy.deepcopy(self._model.curr_state)

        # analyze squares to perform a move or jump.
        idx = 0
        moves_len = len(moves)
        while idx < moves_len:
            squares, annotation = moves[idx]
            delta = abs(squares[0] - squares[1])
            if self._is_move(delta):
                self._try_move(squares, annotation, state_copy)
            else:
                jumped = self._try_jump(squares, annotation, state_copy)
                if not jumped:
                    raise RuntimeError(f"Bad move at index {idx}")
        moves.reverse()
        return moves
