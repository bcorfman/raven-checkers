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
        self._move_check = False
        self._bm_check = False
        self._bk_check = False
        self._wm_check = False
        self._wk_check = False

    def _write_positions(self, f, prefix, positions):
        f.write(prefix + ' ')
        for p in sorted(positions):
            f.write('%d ' % p)
        f.write('\n')

    def _write_moves(self, f):
        f.write('<moves>\n')
        for move in reversed(self.moves):
            start = keymap[move.affected_squares[FIRST][0]]
            dest = keymap[move.affected_squares[LAST][0]]
            movestr = '%d-%d' % (start, dest)
            annotation = move.annotation
            if annotation.startswith(movestr):
                annotation = annotation.replace(movestr, '', 1).rstrip()
            f.write('%s;%s\n' % (movestr, annotation))

    def write(self, filename):
        with open(filename, 'w') as f:
            f.write('<description>\n')
            for line in self.description.splitlines():
                # numbered lists or hyperlinks are not word wrapped.
                if line.startswith('# ') or '[[' in line:
                    f.write(line + '\n')
                    continue
                else:
                    f.write(textwrap.fill(line, 80) + '\n')
            f.write('<setup>\n')
            if self.to_move == WHITE:
                f.write('white_first\n')
            elif self.to_move == BLACK:
                f.write('black_first\n')
            else:
                raise ValueError("Unknown value for to_move variable")
            if 0 <= self.num_players <= 2:
                f.write('%d_player_game\n' % self.num_players)
            else:
                raise ValueError("Unknown value for num_players variable")
            if self.flip_board:
                f.write('flip_board 1\n')
            else:
                f.write('flip_board 0\n')
            self._write_positions(f, 'black_men', self.black_men)
            self._write_positions(f, 'black_kings', self.black_kings)
            self._write_positions(f, 'white_men', self.white_men)
            self._write_positions(f, 'white_kings', self.white_kings)
            self._write_moves(f)

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
                raise IOError('Unrecognized section in file, line %d' % (i+1))

    def _parse_items(self, line):
        men = line.split()[1:]
        return map(int, men)

    def _add_men_to_board(self, locations, val):
        squares = self._model.curr_state.squares
        try:
            for loc in locations:
                idx = square_map[loc]
                squares[idx] = val
        except ValueError:
            raise IOError('Checker location not valid, line %d' % (idx + 1))

    def _parse_setup(self, lines, idx, line_len):
        curr_state = self._model.curr_state
        curr_state.clear()
        idx += 1
        while idx < line_len and '<moves>' not in lines[idx]:
            line = lines[idx].strip().lower()
            if line == 'white_first':
                self.to_move = curr_state.to_move = WHITE
                self._move_check = True
            elif line == 'black_first':
                self.to_move = curr_state.to_move = BLACK
                self._move_check = True
            elif line.endswith('player_game'):
                numstr, _ = line.split('_', 1)
                self.num_players = int(numstr)
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
            raise IOError('Error in <setup> section: not all required items found')
        return idx

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
            if startsq == move.affected_squares[FIRST][0] and destsq == move.affected_squares[LAST][0]:
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
        # small, large = min(start_square, dest_square), max(start_square, dest_square)
        found = False
        for move in legal_moves:
            # a valid jump may either have a single jump in it, or
            # multiple jumps. In the multiple jump case, start_square is the
            # source of the first jump, and dest_square is the endpoint of the
            # last jump.
            if start_square == move.affected_squares[FIRST][0] and dest_square == move.affected_squares[LAST][0]:
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
                raise IOError('Unrecognized section in file, line %d' % (idx+1))

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
