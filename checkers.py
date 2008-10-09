import games, copy, sys
from player import AlphabetaPlayer, HumanPlayer
from globalconst import *

class Checkerboard(object):
    valid_squares = [5,6,7,8,10,11,12,13,14,15,16,17,19,20,21,22,
                     23,24,25,26,28,29,30,31,32,33,34,35,37,38,
                     39,40]
    black_moves = [4,5]
    white_moves = [-4,-5]
    king_moves = [-5,-4,4,5]
    value = [0,0,0,0,0,1,256,0,0,16,4096,0,0,0,0,0,0]
    edge = [5,6,7,8,13,14,22,23,31,32,37,38,39,40]
    center = [15,16,20,21,24,25,29,30]
    row = [0,0,0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,0,3,3,3,3,4,4,4,4,0,
           5,5,5,5,6,6,6,6,0,7,7,7,7]
    safeedge = [8,13,32,37]
    rank = {0:0, 1:-1, 2:1, 3:0, 4:1, 5:1, 6:2, 7:1, 8:1, 9:0,
            10:7, 11:4, 12:2, 13:2, 14:9, 15:8}

    def __init__(self):
        #   (white)
        #            37  38  39  40
        #          32  33  34  35
        #            28  29  30  31
        #          23  24  25  26
        #            19  20  21  22
        #          14  15  16  17
        #            10  11  12  13
        #          5   6   7   8
        #   (black)
        self.squares = [OCCUPIED for i in range(46)]
        s = self.squares
        for i in range(0, 4):
            s[5+i] = s[10+i] = s[14+i] = BLACK | MAN
            s[28+i] = s[32+i] = s[37+i] = WHITE | MAN
            s[19+i] = s[23+i] = FREE
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
        s += "8   %s   %s   %s   %s\n" % (lookup(sq[37]), lookup(sq[38]),
                                   lookup(sq[39]), lookup(sq[40]))
        s += "7 %s   %s   %s   %s\n" % (lookup(sq[32]), lookup(sq[33]),
                                  lookup(sq[34]), lookup(sq[35]))
        s += "6   %s   %s   %s   %s\n" % (lookup(sq[28]), lookup(sq[29]),
                                  lookup(sq[30]), lookup(sq[31]))
        s += "5 %s   %s   %s   %s\n" % (lookup(sq[23]), lookup(sq[24]),
                                  lookup(sq[25]), lookup(sq[26]))
        s += "4   %s   %s   %s   %s\n" % (lookup(sq[19]), lookup(sq[20]),
                                  lookup(sq[21]), lookup(sq[22]))
        s += "3 %s   %s   %s   %s\n" % (lookup(sq[14]), lookup(sq[15]),
                                  lookup(sq[16]), lookup(sq[17]))
        s += "2   %s   %s   %s   %s\n" % (lookup(sq[10]), lookup(sq[11]),
                                  lookup(sq[12]), lookup(sq[13]))
        s += "1 %s   %s   %s   %s\n" % (lookup(sq[5]), lookup(sq[6]),
                                  lookup(sq[7]), lookup(sq[8]))
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
            s[5+i] = s[10+i] = s[14+i] = FREE
            s[19+i] = s[23+i] = FREE
            s[28+i] = s[32+i] = s[37+i] = FREE

    def lookup(self, square):
        return self.charlookup[square & TYPES]

    def count(self, color):
        return sum([1 for i in self.squares if (i & COLORS) == color])

    def get_pieces(self, color):
        if color == BLACK:
            return self.black_pieces
        else:
            return self.white_pieces

    def has_opposition(self, color):
        enemy_color = BLACK if color == WHITE else WHITE
        player_lst = self.find_pieces(color)
        enemy_lst = self.find_pieces(enemy_color)
        if len(player_lst) != len(enemy_lst):
            return False # TODO: revise to handle unequal endgames & pivot men
        pairs = zip(player_lst, enemy_lst)
        td = 0
        for ((i, plr), (j, enemy)) in pairs:
            _, c1 = self.gridmap[i]
            _, c2 = self.gridmap[j]
            td += c1 - c2
        return self.to_move == color and td % 2 == 1

    def is_movable_piece(self, index):
        moves = self.captures or self.moves
        movable_pieces = []
        for move in moves:
            i, _, _ = move[0]
            movable_pieces.append(i)
        return index in movable_pieces

    def can_land_piece(self, plr, src, dest):
        if self.to_move != plr:
            return False
        moves = self.captures or self.moves
        for move in moves:
            start, _, _ = move[0]
            end, _, _ = move[-1]
            if src == start and dest == end:
                return move
        return False

    def make_move(self, move, notify=False, undo=False):
        sq = self.squares
        for m in move:
            idx, oldval, newval = m
            sq[idx] = newval
        if not undo:
            del self._redo_list[:]
            self._undo_list.append(move)
        if self.to_move == BLACK:
            self.to_move = WHITE
        else:
            self.to_move = BLACK

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

            if self.observers:
                for o in self.observers:
                    o.notify(move)
        return self

    def undo_move(self, move=None):
        if move == None:
            if not self._undo_list:
                return
            move = self._undo_list.pop()
            self._redo_list.append(move)
        rmove = [[idx, dest, src] for idx, src, dest in move]
        self.make_move(rmove, True, True)

    def undo_all_moves(self):
        while self._undo_list:
            move = self._undo_list.pop()
            self._redo_list.append(move)
            rmove = [[idx, dest, src] for idx, src, dest in move]
            self.make_move(rmove, True, True)

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

    def _man_capture(self, valid_moves, sq_index, capture_so_far):
        player = self.to_move
        enemy = self.enemy
        squares = self.squares
        for j in valid_moves:
            mid = sq_index+j
            dest = sq_index+j*2
            if (squares[mid] & enemy and
                squares[dest] & FREE):
                sq2 = [mid, squares[mid], FREE]
                if ((player == BLACK and sq_index>=28) or
                    (player == WHITE and sq_index<=17)):
                    sq3 = [dest, FREE, player | KING]
                else:
                    sq3 = [dest, FREE, player | MAN]
                capture_so_far[-1][-1][2] = FREE
                capture_so_far[-1].extend([sq2, sq3])
                return self._man_capture(valid_moves, dest, capture_so_far)
        return capture_so_far

    def _king_capture(self, sq_index, capture_so_far):
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
                capture_so_far[-1][-1][2] = FREE
                capture_so_far[-1].extend([sq2, sq3])
                tmp = squares[sq_index]
                squares[sq_index] = OCCUPIED
                capture_so_far = self._king_capture(dest, capture_so_far)
                squares[sq_index] = tmp
        return capture_so_far

    def _get_captures(self):
        player = self.to_move
        enemy = self.enemy
        squares = self.squares
        if player == WHITE:
            valid_moves = self.white_moves
        else:
            valid_moves = self.black_moves
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
                    if ((player == BLACK and i>=28) or
                        (player == WHITE and i<=17)):
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
        enemy = self.enemy
        squares = self.squares
        if player == WHITE:
            valid_moves = self.white_moves
        else:
            valid_moves = self.black_moves
        moves = []
        for i in self.valid_squares:
            for j in valid_moves:
                dest = i+j
                if (squares[i] & player and
                    squares[i] & MAN and
                    squares[dest] & FREE):
                    sq1 = [i, player | MAN, FREE]
                    if ((player == BLACK and i>=32) or
                        (player == WHITE and i<=13)):
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
        if sq[23] == BLACK | MAN and sq[28] == WHITE | MAN:
            eval += CRAMP
        if sq[22] == WHITE | MAN and sq[17] == BLACK | MAN:
            eval -= CRAMP
        return eval

    def _eval_backrankguard(self, sq):
        eval = 0
        code = 0
        if sq[5] & MAN: code += 1
        if sq[6] & MAN: code += 2
        if sq[7] & MAN: code += 4
        if sq[8] & MAN: code += 8
        backrank = self.rank[code]

        code = 0
        if sq[37] & MAN: code += 8
        if sq[38] & MAN: code += 4
        if sq[39] & MAN: code += 2
        if sq[40] & MAN: code += 1
        backrank = backrank - self.rank[code]
        eval *= BRV * backrank
        return eval

    def _eval_doublecorner(self, sq):
        eval = 0
        if sq[8] == BLACK | MAN:
            if sq[12] == BLACK | MAN or sq[13] == BLACK | MAN:
                eval += INTACTDOUBLECORNER

        if sq[37] == WHITE | MAN:
            if sq[32] == WHITE | MAN or sq[33] == WHITE | MAN:
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
        for i in range(5, 41):
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
        stones_in_system = 0
        tn = nm + nk
        if nwm + nwk - nbk - nbm == 0:
            if self.to_move == BLACK:
                for i in range(5, 9):
                    for j in range(4):
                        if sq[i+9*j] != FREE:
                            stones_in_system += 1
                if stones_in_system % 2:
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
                for i in range(10, 14):
                    for j in range(4):
                        if sq[i+9*j] != FREE:
                            stones_in_system += 1
                if stones_in_system % 2 == 0:
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

    def is_movable_piece(self, index, curr_state=None):
        state = curr_state or self.curr_state
        return state.is_movable_piece(index)

    def can_land_piece(self, plr, src, dest, curr_state=None):
        state = curr_state or self.curr_state
        return state.can_land_piece(plr, src, dest)

    def captures_available(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.captures

    def legal_moves(self, curr_state=None):
        state = curr_state or self.curr_state
        return state.captures or state.moves

    def make_move(self, move, curr_state=None):
        state = curr_state or self.curr_state
        return state.make_move(move, True)

    def undo_move(self, move=None, curr_state=None):
        state = curr_state or self.curr_state
        return state.undo_move(move)

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
        return not state.moves

    def successors(self, curr_state=None, depth=None):
        state = curr_state or self.curr_state
        try:
            try:
                for move in self.legal_moves(state):
                    undone = False
                    self.make_move(move, state)
                    yield move, state
                    self.undo_move(move, state)
                    undone = True
            except GeneratorExit:
                raise
        finally:
            if not undone:
                self.undo_move(move, state)


#def play():
#    game = Checkers()
#    games.play_game(game, HumanPlayer(BLACK), AlphabetaPlayer(WHITE))

#if __name__ == '__main__':
#    play()
