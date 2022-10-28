import copy
import textwrap
from util.globalconst import FIRST, LAST, WHITE, BLACK, MAN, KING, KING_IDX
from util.globalconst import keymap, square_map
from game.checkers import Checkers


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

    def _is_jump(self, delta):
        return delta not in KING_IDX

    def _try_move(self, idx, start, dest, state_copy, annotation):
        legal_moves = self._model.legal_moves(state_copy)
        # match move from file with available moves on checkerboard
        found = False
        startsq, destsq = square_map[start], square_map[dest]
        for move in legal_moves:
            if startsq == move.affected_squares[FIRST][0] and \
               destsq == move.affected_squares[LAST][0]:
                self._model.make_move(move, state_copy, False, False)
                move.annotation = annotation
                self.moves.append(move)
                found = True
                break
        if not found:
            raise IOError('Illegal move found in file, line %d' % (idx+1))

    def _try_jump(self, idx, start, dest, state_copy, annotation):
        if not self._model.captures_available(state_copy):
            return False
        legal_moves = self._model.legal_moves(state_copy)
        # match jump from file with available jumps on checkerboard
        start_square, dest_square = square_map[start], square_map[dest]
        _, _ = min(start_square, dest_square), max(start_square, dest_square)
        # small, large = min(start_square, dest_square), max(start_square,
        # dest_square)
        found = False
        for move in legal_moves:
            # a valid jump may either have a single jump in it, or
            # multiple jumps. In the multiple jump case, start_square is the
            # source of the first jump, and dest_square is the endpoint of the
            # last jump.
            if start_square == move.affected_squares[FIRST][0] and \
               dest_square == move.affected_squares[LAST][0]:
                self._model.make_move(move, state_copy, False, False)
                move.annotation = annotation
                self.moves.append(move)
                found = True
                break
        return found

    def _parse_moves(self, lines, idx, linelen):
        """ Each move in the file lists the beginning and ending square, along
        with an optional annotation string (in Creole fmt) that describes it.
        Since the move listing in the file contains less information than
        we need inside our Checkerboard model, I make sure that each move works
        on a copy of the model before I commit to using it inside the code. """
        state_copy = copy.deepcopy(self._model.curr_state)
        idx += 1
        while idx < linelen:
            line = lines[idx].strip()
            if line == "":
                idx += 1
                continue  # ignore blank lines

            try:
                movestr, annotation = line.split(';', 1)
            except ValueError:
                raise IOError('Unrecognized section in file, line %d' %
                              (idx+1))

            # move is always part of the annotation; I just don't want to
            # have to repeat it explicitly in the file.
            annotation = movestr + annotation

            # analyze affected squares to perform a move or jump.
            start = None
            dest = None
            try:
                start, dest = [int(x) for x in movestr.split('-')]
                delta = square_map[start] - square_map[dest]
            except ValueError:
                raise IOError('Bad move fmt in file, line %d' % idx)
            if self._is_move(delta):
                self._try_move(idx, start, dest, state_copy, annotation)
            else:
                jumped = self._try_jump(idx, start, dest, state_copy,
                                        annotation)
                if not jumped:
                    raise IOError('Bad move fmt in file, line %d' % idx)
            idx += 1
        self.moves.reverse()
        return idx
