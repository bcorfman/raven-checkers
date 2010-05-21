import games
import time
from globalconst import BLACK, WHITE, KING, MAN, OCCUPIED, BLACK_CHAR, WHITE_CHAR
from globalconst import BLACK_KING, WHITE_KING, FREE, OCCUPIED_CHAR, FREE_CHAR
from globalconst import COLORS, TYPES, TURN, CRAMP, BRV, KEV, KCV, MEV, MCV
from globalconst import INTACTDOUBLECORNER, ENDGAME, OPENING, MIDGAME
from globalconst import create_grid_map

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
    valid_squares = [6,7,8,9,12,13,14,15,17,18,19,20,23,24,25,26,
                     28,29,30,31,34,35,36,37,39,40,41,42,45,46,
                     47,48]
    black_moves = [5,6]
    white_moves = [-5,-6]
    king_moves = [-6,-5,5,6]
    # values of pieces (KING, MAN, BLACK, WHITE, FREE)
    value = [0,0,0,0,0,1,256,0,0,16,4096,0,0,0,0,0,0]
    edge = [6,7,8,9,15,17,26,28,37,39,45,46,47,48]
    center = [18,19,24,25,29,30,35,36]
    # values used to calculate tempo -- one for each square on board (0, 48)
    row = [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,2,2,2,2,0,0,3,3,3,3,0,
           4,4,4,4,0,0,5,5,5,5,0,6,6,6,6,0,0,7,7,7,7]
    safeedge = [9,15,39,45]
    rank = {0:0, 1:-1, 2:1, 3:0, 4:1, 5:1, 6:2, 7:1, 8:1, 9:0,
            10:7, 11:4, 12:2, 13:2, 14:9, 15:8}

    def __init__(self):
        self.squares = [OCCUPIED for i in range(56)]
        s = self.squares
        for i in range(0, 4):
            s[6+i] = s[12+i] = s[17+i] = BLACK | MAN
            s[34+i] = s[39+i] = s[45+i] = WHITE | MAN
            s[23+i] = s[28+i] = FREE
        self.to_move = BLACK
        self.charlookup = {BLACK | MAN: BLACK_CHAR, WHITE | MAN: WHITE_CHAR,
                           BLACK | KING: BLACK_KING, WHITE | KING: WHITE_KING,
                           OCCUPIED: OCCUPIED_CHAR, FREE: FREE_CHAR}
        self.observers = []
        self.white_pieces = []
        self.black_pieces = []
        self._undo_list = []
        self._redo_list = []
        self.white_total = 12
        self.black_total = 12
        self.gridmap = create_grid_map()
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
            s[6+i] = s[12+i] = s[17+i] = FREE
            s[23+i] = s[28+i] = FREE
            s[34+i] = s[39+i] = s[45+i] = FREE

    def lookup(self, square):
        return self.charlookup[square & TYPES]

    def count(self, color):
        return self.white_total if color == WHITE else self.black_total

    def get_pieces(self, color):
        return self.black_pieces if color == BLACK else self.white_pieces

    def has_opposition(self, color):
        sq = self.squares
        cols = range(6,10) if self.to_move == BLACK else range(12,16)
        pieces_in_system = 0
        for i in cols:
            for j in range(4):
                if sq[i+11*j] != FREE:
                    pieces_in_system += 1
        return pieces_in_system % 2 == 0

    def row_col_for_index(self, idx):
        return self.gridmap[idx]

    def make_move(self, move, notify=True, undo=True):
        sq = self.squares
        for m in move:
            idx, _, newval = m
            sq[idx] = newval
        if undo:
            del self._redo_list[:]
            self._undo_list.append(move)
        self.to_move ^= COLORS

        if notify:
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

            for o in self.observers:
                o.notify(move)
        return self

    def undo_move(self, move=None, notify=True, redo=True):
        if move == None:
            if not self._undo_list:
                return
            if redo:
                move = self._undo_list.pop()
                self._redo_list.append(move)
        rev_updates = [[idx, dest, src] for idx, src, dest in move]
        self.make_move(rev_updates, notify, redo)

    def undo_all_moves(self):
        while self._undo_list:
            move = self._undo_list.pop()
            self._redo_list.append(move)
            rev_updates = [[idx, dest, src] for idx, src, dest in move]
            self.make_move(rev_updates, True, True)

    def redo_move(self, move=None):
        if move == None:
            if not self._redo_list:
                return
            move = self._redo_list.pop()
            self._undo_list.append(move)
        self.make_move(move, True, True)

    def redo_all_moves(self):
        while self._redo_list:
            move = self._redo_list.pop()
            self._undo_list.append(move)
            self.make_move(move, True, True)

    def reset_undo(self):
        self._undo_list = []
        self._redo_list = []

    def create_game(self, gameinfo):
        pass

    def _man_capture(self, valid_moves, sq_index, move):
        player = self.to_move
        enemy = self.enemy
        squares = self.squares
        for j in valid_moves:
            mid = sq_index+j
            dest = sq_index+j*2
            if (squares[mid] & enemy and
                squares[dest] & FREE):
                sq2 = [mid, squares[mid], FREE]
                if ((player == BLACK and sq_index>=34) or
                    (player == WHITE and sq_index<=20)):
                    sq3 = [dest, FREE, player | KING]
                else:
                    sq3 = [dest, FREE, player | MAN]
                move[-1][2] = FREE
                move.extend([sq2, sq3])
                move = self._man_capture(valid_moves, dest, move)
        return move

    def _king_capture(self, sq_index, move):
        player = self.to_move
        enemy = self.enemy
        squares = self.squares
        for j in self.king_moves:
            mid = sq_index+j
            dest = sq_index+j*2
            if (squares[mid] & enemy and
                squares[dest] & FREE):
                sq2 = [mid, squares[mid], FREE]
                sq3 = [dest, squares[dest], player | KING]
                move[-1][2] = FREE
                move.extend([sq2, sq3])
                tmp = squares[sq_index]
                squares[sq_index] = OCCUPIED
                move = self._king_capture(dest, move)
                squares[sq_index] = tmp
        return move

    def _get_captures(self):
        player = self.to_move
        enemy = self.enemy
        squares = self.squares
        valid_moves = self.white_moves if player == WHITE else self.black_moves
        captures = []
        for i in self.valid_squares:
            for j in valid_moves:
                mid = i+j
                dest = i+j*2
                if (squares[i] & player and
                    squares[i] & MAN and
                    squares[mid] & enemy and
                    squares[dest] & FREE):
                    sq1 = [i, player | MAN, FREE]
                    sq2 = [mid, squares[mid], FREE]
                    if ((player == BLACK and i>=34) or
                        (player == WHITE and i<=20)):
                        sq3 = [dest, FREE, player | KING]
                    else:
                        sq3 = [dest, FREE, player | MAN]
                    captures.append([sq1, sq2, sq3])
                    captures = self._man_capture(valid_moves, dest, captures)
            for j in self.king_moves:
                mid = i+j
                dest = i+j*2
                if (squares[i] & player and
                    squares[i] & KING and
                    squares[mid] & enemy and
                    squares[dest] & FREE):
                    sq1 = [i, player | KING, FREE]
                    sq2 = [mid, squares[mid], FREE]
                    sq3 = [dest, squares[dest], player | KING]
                    captures.append([sq1, sq2, sq3])
                    tmp1, tmp2 = squares[i], squares[mid]
                    squares[i], squares[mid] = FREE, FREE
                    captures = self._king_capture(dest, captures)
                    squares[i], squares[mid] = tmp1, tmp2
        return captures
    captures = property(_get_captures,
                        doc="Forced captures for the current player")

    def _get_moves(self):
        player = self.to_move
        squares = self.squares
        valid_moves = self.white_moves if player == WHITE else self.black_moves
        moves = []
        for i in self.valid_squares:
            for j in valid_moves:
                dest = i+j
                if (squares[i] & player and
                    squares[i] & MAN and
                    squares[dest] & FREE):
                    sq1 = [i, player | MAN, FREE]
                    if ((player == BLACK and i>=39) or
                        (player == WHITE and i<=15)):
                        sq2 = [dest, FREE, player | KING]
                    else:
                        sq2 = [dest, FREE, player | MAN]
                    moves.append([sq1, sq2])
            for j in self.king_moves:
                dest = i+j
                if (squares[i] & player and
                    squares[i] & KING and
                    squares[dest] & FREE):
                    sq1 = [i, player | KING, FREE]
                    sq2 = [dest, FREE, player | KING]
                    moves.append([sq1, sq2])
        return moves
    moves = property(_get_moves,
                        doc="Available moves for the current player")

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

        eval = v1 - v2 # material values
        # favor exchanges if in material plus
        eval += (250 * (v1 - v2))/(v1 + v2)

        nm = nbm + nwm
        nk = nbk + nwk

        # fine evaluation below
        if player == BLACK:
            eval += TURN
            mult = -1
        else:
            eval -= TURN
            mult = 1

        return mult * \
                (eval + self._eval_cramp(sq) + self._eval_backrankguard(sq) +
                self._eval_doublecorner(sq) + self._eval_center(sq) +
                self._eval_edge(sq) +
                self._eval_tempo(sq, nm, nbk, nbm, nwk, nwm) +
                self._eval_playeropposition(sq, nwm, nwk, nbk, nbm, nm, nk))

    def _eval_cramp(self, sq):
        eval = 0
        if sq[28] == BLACK | MAN and sq[34] == WHITE | MAN:
            eval += CRAMP
        if sq[26] == WHITE | MAN and sq[20] == BLACK | MAN:
            eval -= CRAMP
        return eval

    def _eval_backrankguard(self, sq):
        eval = 0
        code = 0
        if sq[6] & MAN: code += 1
        if sq[7] & MAN: code += 2
        if sq[8] & MAN: code += 4
        if sq[9] & MAN: code += 8
        backrank = self.rank[code]

        code = 0
        if sq[45] & MAN: code += 8
        if sq[46] & MAN: code += 4
        if sq[47] & MAN: code += 2
        if sq[48] & MAN: code += 1
        backrank = backrank - self.rank[code]
        eval *= BRV * backrank
        return eval

    def _eval_doublecorner(self, sq):
        eval = 0
        if sq[9] == BLACK | MAN:
            if sq[14] == BLACK | MAN or sq[15] == BLACK | MAN:
                eval += INTACTDOUBLECORNER

        if sq[45] == WHITE | MAN:
            if sq[39] == WHITE | MAN or sq[40] == WHITE | MAN:
                eval -= INTACTDOUBLECORNER
        return eval

    def _eval_center(self, sq):
        eval = 0
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
        eval += (nbmc-nwmc) * MCV
        eval += (nbkc-nwkc) * KCV
        return eval

    def _eval_edge(self, sq):
        eval = 0
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
        eval -= (nbme-nwme) * MEV
        eval -= (nbke-nwke) * KEV
        return eval

    def _eval_tempo(self, sq, nm, nbk, nbm, nwk, nwm):
        eval = tempo = 0
        for i in range(6, 49):
            if sq[i] == BLACK | MAN:
                tempo += self.row[i]
            if sq[i] == WHITE | MAN:
                tempo -= 7 - self.row[i]

        if nm >= 16:
            eval += OPENING * tempo
        if nm <= 15 and nm >= 12:
            eval += MIDGAME * tempo
        if nm < 9:
            eval += ENDGAME * tempo

        for s in self.safeedge:
            if nbk + nbm > nwk + nwm and nwk < 3:
                if sq[s] == WHITE | KING:
                    eval -= 15
            if nwk + nwm > nbk + nbm and nbk < 3:
                if sq[s] == BLACK | KING:
                    eval += 15
        return eval

    def _eval_playeropposition(self, sq, nwm, nwk, nbk, nbm, nm, nk):
        eval = 0
        pieces_in_system = 0
        tn = nm + nk
        if nwm + nwk - nbk - nbm == 0:
            if self.to_move == BLACK:
                for i in range(6, 10):
                    for j in range(4):
                        if sq[i+11*j] != FREE:
                            pieces_in_system += 1
                if pieces_in_system % 2:
                    if tn <= 12: eval += 1
                    if tn <= 10: eval += 1
                    if tn <= 8: eval += 2
                    if tn <= 6: eval += 2
                else:
                    if tn <= 12: eval -= 1
                    if tn <= 10: eval -= 1
                    if tn <= 8: eval -= 2
                    if tn <= 6: eval -= 2
            else:
                for i in range(12, 16):
                    for j in range(4):
                        if sq[i+11*j] != FREE:
                            pieces_in_system += 1
                if pieces_in_system % 2 == 0:
                    if tn <= 12: eval += 1
                    if tn <= 10: eval += 1
                    if tn <= 8: eval += 2
                    if tn <= 6: eval += 2
                else:
                    if tn <= 12: eval -= 1
                    if tn <= 10: eval -= 1
                    if tn <= 8: eval -= 2
                    if tn <= 6: eval -= 2
        return eval


class Checkers(games.Game):
    def __init__(self):
        self.curr_state = Checkerboard()

    def captures_available(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.captures

    def legal_moves(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.captures or state.moves

    def make_move(self, move, curr_state=None, notify=True):
        state = curr_state or self.curr_state
        return state.make_move(move, notify)

    def undo_move(self, move=None, curr_state=None, notify=True, redo=True):
        state = curr_state or self.curr_state
        return state.undo_move(move, notify, redo)

    def undo_all_moves(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.undo_all_moves()

    def redo_move(self, move=None, curr_state=None):
        state = curr_state or self.curr_state
        return state.redo_move(move)

    def redo_all_moves(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.redo_all_moves()

    def utility(self, player, curr_state=None):
        state = curr_state or self.curr_state
        return state.utility(player)

    def terminal_test(self, curr_state=None):
        state = curr_state or self.curr_state
        return not self.legal_moves(state)

    def successors(self, curr_state=None):
        state = curr_state or self.curr_state
        moves = self.legal_moves(state)
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
            nodes += self.perft(depth-1, state)
            state.undo_move(move, False, False)
        return nodes


def play():
    game = Checkers()
    for depth in range(1, 9):
        start = time.time()
        print "Perft for depth %d: %d. Time: %5.3f sec" % (depth,
                                                           game.perft(depth),
                                                           time.time() - start)

if __name__ == '__main__':
    play()
