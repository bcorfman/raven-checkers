import ai.games as games
import time
from base.move import Move
from util.globalconst import BLACK, WHITE, KING, MAN, OCCUPIED, BLACK_CHAR, WHITE_CHAR
from util.globalconst import BLACK_KING, WHITE_KING, FREE, OCCUPIED_CHAR, FREE_CHAR
from util.globalconst import COLORS, TYPES, TURN, CRAMP, BRV, KEV, KCV, MEV, MCV
from util.globalconst import INTACT_DOUBLE_CORNER, ENDGAME, OPENING, MIDGAME
from util.globalconst import create_grid_map, KING_IDX, BLACK_IDX, WHITE_IDX


class Checkerboard(object):
    #   (white)
    #            45  46  47  48
    #          39  40  41  42
    #            34  35  36  37
    #          28  29  30  31
    #            23  24  25  26
    #          17  18  19  20
    #            12  13  14  15
    #          6   7   8   9
    #   (black)
    valid_squares = [6, 7, 8, 9, 12, 13, 14, 15, 17, 18, 19, 20, 23, 24, 25, 26,
                     28, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42, 45, 46,
                     47, 48]
    # values of pieces (KING, MAN, BLACK, WHITE, FREE)
    value = [0, 0, 0, 0, 0, 1, 256, 0, 0, 16, 4096, 0, 0, 0, 0, 0, 0]
    edge = [6, 7, 8, 9, 15, 17, 26, 28, 37, 39, 45, 46, 47, 48]
    center = [18, 19, 24, 25, 29, 30, 35, 36]
    # values used to calculate tempo -- one for each square on board (0, 48)
    row = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 0,
           4, 4, 4, 4, 0, 0, 5, 5, 5, 5, 0, 6, 6, 6, 6, 0, 0, 7, 7, 7, 7]
    safe_edge = [9, 15, 39, 45]
    rank = {0: 0, 1: -1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 2, 7: 1, 8: 1, 9: 0,
            10: 7, 11: 4, 12: 2, 13: 2, 14: 9, 15: 8}

    def __init__(self):
        self.squares = [OCCUPIED for _ in range(56)]
        s = self.squares
        for i in range(0, 4):
            s[6 + i] = s[12 + i] = s[17 + i] = BLACK | MAN
            s[34 + i] = s[39 + i] = s[45 + i] = WHITE | MAN
            s[23 + i] = s[28 + i] = FREE
        self.to_move = BLACK
        self.char_lookup = {BLACK | MAN: BLACK_CHAR, WHITE | MAN: WHITE_CHAR,
                            BLACK | KING: BLACK_KING, WHITE | KING: WHITE_KING,
                            OCCUPIED: OCCUPIED_CHAR, FREE: FREE_CHAR}
        self.observers = []
        self.white_pieces = []
        self.black_pieces = []
        self.undo_list = []
        self.redo_list = []
        self.white_total = 12
        self.black_total = 12
        self.grid_map = create_grid_map()
        self.ok_to_move = True

    def __repr__(self):
        bc = self.count(BLACK)
        wc = self.count(WHITE)
        sq = self.squares
        lookup = self.lookup
        s = "[%s=%2d %s=%2d (%+d)]\n" % (BLACK_CHAR, bc,
                                         WHITE_CHAR, wc,
                                         bc - wc)
        s += "8   %s   %s   %s   %s\n" % (lookup(sq[45]), lookup(sq[46]),
                                          lookup(sq[47]), lookup(sq[48]))
        s += "7 %s   %s   %s   %s\n" % (lookup(sq[39]), lookup(sq[40]),
                                        lookup(sq[41]), lookup(sq[42]))
        s += "6   %s   %s   %s   %s\n" % (lookup(sq[34]), lookup(sq[35]),
                                          lookup(sq[36]), lookup(sq[37]))
        s += "5 %s   %s   %s   %s\n" % (lookup(sq[28]), lookup(sq[29]),
                                        lookup(sq[30]), lookup(sq[31]))
        s += "4   %s   %s   %s   %s\n" % (lookup(sq[23]), lookup(sq[24]),
                                          lookup(sq[25]), lookup(sq[26]))
        s += "3 %s   %s   %s   %s\n" % (lookup(sq[17]), lookup(sq[18]),
                                        lookup(sq[19]), lookup(sq[20]))
        s += "2   %s   %s   %s   %s\n" % (lookup(sq[12]), lookup(sq[13]),
                                          lookup(sq[14]), lookup(sq[15]))
        s += "1 %s   %s   %s   %s\n" % (lookup(sq[6]), lookup(sq[7]),
                                        lookup(sq[8]), lookup(sq[9]))
        s += "  a b c d e f g h"
        return s

    def _get_enemy(self):
        if self.to_move == BLACK:
            return WHITE
        return BLACK

    enemy = property(_get_enemy,
                     doc="The color for the player that doesn't have the current turn")

    def attach(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def detach(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def clear(self):
        s = self.squares
        for i in range(0, 4):
            s[6 + i] = s[12 + i] = s[17 + i] = FREE
            s[23 + i] = s[28 + i] = FREE
            s[34 + i] = s[39 + i] = s[45 + i] = FREE

    def lookup(self, square):
        return self.char_lookup[square & TYPES]

    def count(self, color):
        return self.white_total if color == WHITE else self.black_total

    def get_pieces(self, color):
        return self.black_pieces if color == BLACK else self.white_pieces

    def has_opposition(self, color):
        sq = self.squares
        cols = range(6, 10) if self.to_move == BLACK else range(12, 16)
        pieces_in_system = 0
        for i in cols:
            for j in range(4):
                if sq[i + 11 * j] != FREE:
                    pieces_in_system += 1
        return pieces_in_system % 2 == 1

    def row_col_for_index(self, idx):
        return self.grid_map[idx]

    def update_piece_count(self):
        self.white_pieces = []
        for i, piece in enumerate(self.squares):
            if piece & COLORS == WHITE:
                self.white_pieces.append((i, piece))

        self.black_pieces = []
        for i, piece in enumerate(self.squares):
            if piece & COLORS == BLACK:
                self.black_pieces.append((i, piece))

        self.white_total = len(self.white_pieces)
        self.black_total = len(self.black_pieces)

    def delete_redo_list(self):
        del self.redo_list[:]

    def make_move(self, move, notify=True, undo=True, annotation=''):
        sq = self.squares
        for idx, _, new_value in move.affected_squares:
            sq[idx] = new_value
        self.to_move ^= COLORS

        if notify:
            self.update_piece_count()
            for o in self.observers:
                o.notify(move)
        if undo:
            move.annotation = annotation
            self.undo_list.append(move)
        return self

    def undo_move(self, move=None, notify=True, redo=True, annotation=''):
        if move is None:
            if not self.undo_list:
                return
            if redo:
                move = self.undo_list.pop()
        rev_move = Move([[idx, dest, src] for idx, src, dest
                         in move.affected_squares])
        rev_move.annotation = move.annotation
        self.make_move(rev_move, notify, False)
        if redo:
            move.annotation = annotation
            self.redo_list.append(move)

    def undo_all_moves(self, annotation=''):
        while self.undo_list:
            move = self.undo_list.pop()
            rev_move = Move([[idx, dest, src] for idx, src, dest
                             in move.affected_squares])
            rev_move.annotation = move.annotation
            self.make_move(rev_move, True, False)
            move.annotation = annotation
            self.redo_list.append(move)
            annotation = rev_move.annotation

    def redo_move(self, move=None, annotation=''):
        if move is None:
            if not self.redo_list:
                return
            move = self.redo_list.pop()
        self.make_move(move, True, True, annotation)

    def redo_all_moves(self, annotation=''):
        while self.redo_list:
            move = self.redo_list.pop()
            next_annotation = move.annotation
            self.make_move(move, True, True, annotation)
            annotation = next_annotation

    def reset_undo(self):
        self.undo_list = []
        self.redo_list = []

    def utility(self, player):
        """ Player evaluation function """
        sq = self.squares
        code = sum(self.value[s] for s in sq)
        nwm = code % 16
        nwk = (code >> 4) % 16
        nbm = (code >> 8) % 16
        nbk = (code >> 12) % 16

        v1 = 100 * nbm + 130 * nbk
        v2 = 100 * nwm + 130 * nwk

        evaluation = v1 - v2  # material values
        # favor exchanges if in material plus
        evaluation += (250 * (v1 - v2)) / (v1 + v2)

        nm = nbm + nwm
        nk = nbk + nwk

        # fine evaluation below
        if player == BLACK:
            evaluation += TURN
            multiplier = -1
        else:
            evaluation -= TURN
            multiplier = 1

        return multiplier * (evaluation + self._eval_cramp(sq) + self._eval_back_rank_guard(sq) +
                             self._eval_double_corner(sq) + self._eval_center(sq) + self._eval_edge(sq) +
                             self._eval_tempo(sq, nm, nbk, nbm, nwk, nwm) +
                             self._eval_player_opposition(sq, nwm, nwk, nbk, nbm, nm, nk))

    def _extend_capture(self, valid_moves, captures, add_sq_func, visited):
        player = self.to_move
        enemy = self.enemy
        squares = self.squares
        final_captures = []
        capture = None
        while captures:
            c = captures.pop()
            new_captures = []
            for j in valid_moves:
                capture = c.affected_squares[:]
                last_pos = capture[-1][0]
                mid = last_pos + j
                dest = last_pos + j * 2
                if ((last_pos, mid, dest) not in visited and
                        (dest, mid, last_pos) not in visited and
                        squares[mid] & enemy and
                        squares[dest] & FREE):
                    sq2, sq3 = add_sq_func(player, squares, mid, dest, last_pos)
                    capture[-1][2] = FREE
                    capture.extend([sq2, sq3])
                    visited.add((last_pos, mid, dest))
                    new_captures.append(Move(capture))
            if new_captures:
                captures.extend(new_captures)
            else:
                final_captures.append(Move(capture))
        return final_captures

    def _capture_man(self, player, squares, mid, dest, last_pos):
        sq2 = [mid, squares[mid], FREE]
        if ((player == BLACK and last_pos >= 34) or
                (player == WHITE and last_pos <= 20)):
            sq3 = [dest, FREE, player | KING]
        else:
            sq3 = [dest, FREE, player | MAN]
        return sq2, sq3

    def _capture_king(self, player, squares, mid, dest, last_pos):
        sq2 = [mid, squares[mid], FREE]
        sq3 = [dest, squares[dest], player | KING]
        return sq2, sq3

    def _get_captures(self):
        player = self.to_move
        enemy = self.enemy
        squares = self.squares
        valid_indices = WHITE_IDX if player == WHITE else BLACK_IDX
        all_captures = []
        for i in self.valid_squares:
            if squares[i] & player and squares[i] & MAN:
                for j in valid_indices:
                    mid = i + j
                    dest = i + j * 2
                    if squares[mid] & enemy and squares[dest] & FREE:
                        sq1 = [i, player | MAN, FREE]
                        sq2 = [mid, squares[mid], FREE]
                        if ((player == BLACK and i >= 34) or
                                (player == WHITE and i <= 20)):
                            sq3 = [dest, FREE, player | KING]
                        else:
                            sq3 = [dest, FREE, player | MAN]
                        capture = [Move([sq1, sq2, sq3])]
                        visited = set()
                        visited.add((i, mid, dest))
                        temp = squares[i]
                        squares[i] = FREE
                        captures = self._extend_capture(valid_indices,
                                                        capture,
                                                        self._capture_man,
                                                        visited)
                        squares[i] = temp
                        all_captures.extend(captures)
            if squares[i] & player and squares[i] & KING:
                for j in KING_IDX:
                    mid = i + j
                    dest = i + j * 2
                    if squares[mid] & enemy and squares[dest] & FREE:
                        sq1 = [i, player | KING, FREE]
                        sq2 = [mid, squares[mid], FREE]
                        sq3 = [dest, squares[dest], player | KING]
                        capture = [Move([sq1, sq2, sq3])]
                        visited = set()
                        visited.add((i, mid, dest))
                        temp = squares[i]
                        squares[i] = FREE
                        captures = self._extend_capture(KING_IDX,
                                                        capture,
                                                        self._capture_king,
                                                        visited)
                        squares[i] = temp
                        all_captures.extend(captures)
        return all_captures

    captures = property(_get_captures,
                        doc="Forced captures for the current player")

    def _get_moves(self):
        player = self.to_move
        squares = self.squares
        valid_indices = WHITE_IDX if player == WHITE else BLACK_IDX
        moves = []
        for i in self.valid_squares:
            for j in valid_indices:
                dest = i + j
                if (squares[i] & player and
                        squares[i] & MAN and
                        squares[dest] & FREE):
                    sq1 = [i, player | MAN, FREE]
                    if ((player == BLACK and i >= 39) or
                            (player == WHITE and i <= 15)):
                        sq2 = [dest, FREE, player | KING]
                    else:
                        sq2 = [dest, FREE, player | MAN]
                    moves.append(Move([sq1, sq2]))
            for j in KING_IDX:
                dest = i + j
                if (squares[i] & player and
                        squares[i] & KING and
                        squares[dest] & FREE):
                    sq1 = [i, player | KING, FREE]
                    sq2 = [dest, FREE, player | KING]
                    moves.append(Move([sq1, sq2]))
        return moves

    moves = property(_get_moves,
                     doc="Available moves for the current player")

    def _eval_cramp(self, sq):
        evaluation = 0
        if sq[28] == BLACK | MAN and sq[34] == WHITE | MAN:
            evaluation += CRAMP
        if sq[26] == WHITE | MAN and sq[20] == BLACK | MAN:
            evaluation -= CRAMP
        return evaluation

    def _eval_back_rank_guard(self, sq):
        evaluation = 0
        code = 0
        if sq[6] & MAN:
            code += 1
        if sq[7] & MAN:
            code += 2
        if sq[8] & MAN:
            code += 4
        if sq[9] & MAN:
            code += 8
        back_rank = self.rank[code]

        code = 0
        if sq[45] & MAN:
            code += 8
        if sq[46] & MAN:
            code += 4
        if sq[47] & MAN:
            code += 2
        if sq[48] & MAN:
            code += 1
        back_rank = back_rank - self.rank[code]
        evaluation *= BRV * back_rank
        return evaluation

    def _eval_double_corner(self, sq):
        evaluation = 0
        if sq[9] == BLACK | MAN:
            if sq[14] == BLACK | MAN or sq[15] == BLACK | MAN:
                evaluation += INTACT_DOUBLE_CORNER

        if sq[45] == WHITE | MAN:
            if sq[39] == WHITE | MAN or sq[40] == WHITE | MAN:
                evaluation -= INTACT_DOUBLE_CORNER
        return evaluation

    def _eval_center(self, sq):
        evaluation = 0
        nbmc = nbkc = nwmc = nwkc = 0
        for c in self.center:
            if sq[c] != FREE:
                if sq[c] == BLACK | MAN:
                    nbmc += 1
                if sq[c] == BLACK | KING:
                    nbkc += 1
                if sq[c] == WHITE | MAN:
                    nwmc += 1
                if sq[c] == WHITE | KING:
                    nwkc += 1
        evaluation += (nbmc - nwmc) * MCV
        evaluation += (nbkc - nwkc) * KCV
        return evaluation

    def _eval_edge(self, sq):
        evaluation = 0
        nbme = nbke = nwme = nwke = 0
        for e in self.edge:
            if sq[e] != FREE:
                if sq[e] == BLACK | MAN:
                    nbme += 1
                if sq[e] == BLACK | KING:
                    nbke += 1
                if sq[e] == WHITE | MAN:
                    nwme += 1
                if sq[e] == WHITE | KING:
                    nwke += 1
        evaluation -= (nbme - nwme) * MEV
        evaluation -= (nbke - nwke) * KEV
        return evaluation

    def _eval_tempo(self, sq, nm, nbk, nbm, nwk, nwm):
        evaluation = tempo = 0
        for i in range(6, 49):
            if sq[i] == BLACK | MAN:
                tempo += self.row[i]
            if sq[i] == WHITE | MAN:
                tempo -= 7 - self.row[i]

        if nm >= 16:
            evaluation += OPENING * tempo
        if 15 >= nm >= 12:
            evaluation += MIDGAME * tempo
        if nm < 9:
            evaluation += ENDGAME * tempo

        for s in self.safe_edge:
            if nbk + nbm > nwk + nwm and nwk < 3 and sq[s] == WHITE | KING:
                evaluation -= 15
            if nwk + nwm > nbk + nbm and nbk < 3 and sq[s] == BLACK | KING:
                evaluation += 15
        return evaluation

    def _eval_player_opposition(self, sq, nwm, nwk, nbk, nbm, nm, nk):
        evaluation = 0
        pieces_in_system = 0
        tn = nm + nk
        if nwm + nwk - nbk - nbm == 0:
            if self.to_move == BLACK:
                for i in range(6, 10):
                    for j in range(4):
                        if sq[i + 11 * j] != FREE:
                            pieces_in_system += 1
                if pieces_in_system % 2:
                    if tn <= 12:
                        evaluation += 1
                    if tn <= 10:
                        evaluation += 1
                    if tn <= 8:
                        evaluation += 2
                    if tn <= 6:
                        evaluation += 2
                else:
                    if tn <= 12:
                        evaluation -= 1
                    if tn <= 10:
                        evaluation -= 1
                    if tn <= 8:
                        evaluation -= 2
                    if tn <= 6:
                        evaluation -= 2
            else:
                for i in range(12, 16):
                    for j in range(4):
                        if sq[i + 11 * j] != FREE:
                            pieces_in_system += 1
                if pieces_in_system % 2 == 0:
                    if tn <= 12:
                        evaluation += 1
                    if tn <= 10:
                        evaluation += 1
                    if tn <= 8:
                        evaluation += 2
                    if tn <= 6:
                        evaluation += 2
                else:
                    if tn <= 12:
                        evaluation -= 1
                    if tn <= 10:
                        evaluation -= 1
                    if tn <= 8:
                        evaluation -= 2
                    if tn <= 6:
                        evaluation -= 2
        return evaluation


class Checkers(games.Game):
    def __init__(self):
        games.Game.__init__(self)
        self.curr_state = Checkerboard()

    def captures_available(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.captures

    def legal_moves(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.captures or state.moves

    def make_move(self, move, curr_state=None, notify=True, undo=True,
                  annotation=''):
        state = curr_state or self.curr_state
        return state.make_move(move, notify, undo, annotation)

    def undo_move(self, move=None, curr_state=None, notify=True, redo=True,
                  annotation=''):
        state = curr_state or self.curr_state
        return state.undo_move(move, notify, redo, annotation)

    def undo_all_moves(self, curr_state=None, annotation=''):
        state = curr_state or self.curr_state
        return state.undo_all_moves(annotation)

    def redo_move(self, move=None, curr_state=None, annotation=''):
        state = curr_state or self.curr_state
        return state.redo_move(move, annotation)

    def redo_all_moves(self, curr_state=None, annotation=''):
        state = curr_state or self.curr_state
        return state.redo_all_moves(annotation)

    def utility(self, player, curr_state=None):
        state = curr_state or self.curr_state
        return state.utility(player)

    def terminal_test(self, curr_state=None):
        state = curr_state or self.curr_state
        return not self.legal_moves(state)

    def successors(self, curr_state=None):
        move = None
        state = curr_state or self.curr_state
        moves = self.legal_moves(state)
        if not moves:
            yield [], state
        else:
            undone = False
            try:
                try:
                    for move in moves:
                        undone = False
                        self.make_move(move, state, False)
                        yield move, state
                        self.undo_move(move, state, False)
                        undone = True
                except GeneratorExit:
                    raise
            finally:
                if moves and not undone:
                    self.undo_move(move, state, False)

    def perft(self, depth, curr_state=None):
        if depth == 0:
            return 1

        state = curr_state or self.curr_state
        nodes = 0
        for move in self.legal_moves(state):
            state.make_move(move, False, False)
            nodes += self.perft(depth - 1, state)
            state.undo_move(move, False, False)
        return nodes


def play():
    game = Checkers()
    for depth in range(1, 11):
        start = time.time()
        print("Perft for depth %d: %d. Time: %5.3f sec" % (depth,
                                                           game.perft(depth),
                                                           time.time() - start))


if __name__ == '__main__':
    play()
