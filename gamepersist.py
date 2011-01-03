import copy
from globalconst import *
from move import Move
from checkers import Checkers

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
        self._move_check = False
        self._bm_check = False
        self._bk_check = False
        self._wm_check = False
        self._wk_check = False

    def read(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        linelen = len(lines)
        i = 0
        while True:
            if i >= linelen:
                break

            line = lines[i].strip()
            if line.startswith('<description>'):
                self.description = ''
                i += 1
                while i < linelen and not lines[i].startswith('<setup>'):
                    self.description += lines[i]
                    i += 1
            elif line.startswith('<setup>'):
                i = self._parse_setup(lines, i, linelen)
            elif line.startswith('<moves>'):
                i = self._parse_moves(lines, i, linelen)
            else:
                raise IOError, 'Unrecognized section in file, line %d' % i

    def _parse_items(self, line):
        men = line.split()[1:]
        return map(int, men)

    def _add_men_to_board(self, locations, val):
        squares = self._model.curr_state.squares
        try:
            for loc in locations:
                idx = squaremap[loc]
                squares[idx] = val
        except ValueError:
            raise IOError, 'Checker location not valid, line %d' % i

    def _parse_setup(self, lines, idx, linelen):
        curr_state = self._model.curr_state
        curr_state.clear()
        idx += 1
        while idx < linelen and '<moves>' not in lines[idx]:
            line = lines[idx].strip().lower()
            if line == 'white_first':
                self.to_move = curr_state.to_move = WHITE
                self._move_check = True
            elif line == 'black_first':
                self.to_move = curr_state.to_move = BLACK
                self._move_check = True
            elif line.startswith('flip_board'):
                _, setting = line.split()
                val = int(setting)
                self.flip_board = True if val else False
            elif line.startswith('black_men'):
                self.black_men = self._parse_items(line)
                self._add_men_to_board(self.black_men, BLACK | MAN)
                self._bm_check = True
            elif line.startswith('white_men'):
                self.white_men = self._parse_items(line)
                self._add_men_to_board(self.white_men, WHITE | MAN)
                self._wm_check = True
            elif line.startswith('black_kings'):
                self.black_kings = self._parse_items(line)
                self._add_men_to_board(self.black_kings, BLACK | KING)
                self._bk_check = True
            elif line.startswith('white_kings'):
                self.white_kings = self._parse_items(line)
                self._add_men_to_board(self.white_kings, WHITE | KING)
                self._wk_check = True
            idx += 1
        if (not self._move_check and not self._bm_check and not self._wm_check
            and not self._bk_check and not self._wk_check):
            raise IOError, 'Error in <setup> section: not all required items found'
        return idx

    def _is_move(self, delta):
        return delta in KING_IDX

    def _is_jump(self, delta):
        """ A jump is twice as far as a move. """
        return delta in [x*2 for x in KING_IDX]

    def _try_move(self, idx, start, dest, state_copy, annotation):
        legal_moves = self._model.legal_moves(state_copy)
        # match move from file with available moves on checkerboard
        found = False
        startsq, destsq = squaremap[start], squaremap[dest]
        for move in legal_moves:
            if (startsq == move.affected_squares[FIRST][0] and
                destsq == move.affected_squares[LAST][0]):
                self._model.make_move(move, state_copy, False, False)
                move.annotation = annotation
                self.moves.append(move)
                found = True
                break
        if not found:
            raise IOError, 'Illegal move found in file, line %d' % idx

    def _try_jump(self, idx, start, dest, state_copy, annotation):
        legal_moves = self._model.legal_moves(state_copy)
        # match jump from file with available jumps on checkerboard
        startsq, destsq = squaremap[start], squaremap[dest]
        small, large = min(startsq, destsq), max(startsq, destsq)
        midsq = small + (large-small) / 2
        found = False
        for move in legal_moves:
            if (self._model.captures_available(state_copy) and
                startsq == move.affected_squares[FIRST][0] and
                midsq == move.affected_squares[MID][0] and
                destsq == move.affected_squares[LAST][0]):
                self._model.make_move(move, state_copy, False, False)
                move.annotation = annotation
                self.moves.append(move)
                found = True
                break
        if not found:
            raise IOError, 'Illegal move found in file, line %d' % idx

    def _parse_moves(self, lines, idx, linelen):
        """ Each move in the file lists the beginning and ending square, along
        with an optional annotation string (in Creole format) that describes it.
        Since the move listing in the file contains less information than
        we need inside our Checkerboard model, I make sure that each move works
        on a copy of the model before I commit to using it inside the code. """
        state_copy = copy.deepcopy(self._model.curr_state)
        idx += 1
        while idx < linelen:
            line = lines[idx].strip()
            if line == "":
                continue # ignore blank lines

            try:
                movestr, annotation = line.split(';', 1)
            except ValueError:
                raise IOError, 'Unrecognized section in file, line %d' % idx

            # move is always part of the annotation; I just don't want to
            # have to repeat it explicitly in the file.
            annotation = movestr + annotation

            # analyze affected squares to perform a move or jump.
            try:
                start, dest = [int(x) for x in movestr.split('-')]
            except ValueError:
                raise IOError, 'Bad move format in file, line %d' % idx
            delta = squaremap[start] - squaremap[dest]
            if self._is_move(delta):
                self._try_move(idx, start, dest, state_copy, annotation)
            elif self._is_jump(delta):
                self._try_jump(idx, start, dest, state_copy, annotation)
            else:
                raise IOError, 'Bad move format in file, line %d' % idx
            idx += 1
        self.moves.reverse()
        return idx
