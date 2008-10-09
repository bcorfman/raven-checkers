DEFAULT_SIZE = 400
BOARD_SIZE = 8
CHECKER_SIZE = 30

MOVE = 0
JUMP = 1

OCCUPIED = 0
BLACK = 1
WHITE = 2
MAN = 4
KING = 8
FREE = 16
COLORS = BLACK | WHITE
TYPES = OCCUPIED | BLACK | WHITE | MAN | KING | FREE

HUMAN = 0
COMPUTER = 1

MIN = 0
MAX = 1

START = 0
MID = 1
END = 2

CROWN_IMAGE = 'crown.gif'
LIGHT_SQUARES = 'tan'
DARK_SQUARES = 'dark green'
OUTLINE_COLOR = 'white'
LIGHT_CHECKERS = 'white'
DARK_CHECKERS = 'red'
WHITE_CHAR = 'w'
WHITE_KING = 'W'
BLACK_CHAR = 'b'
BLACK_KING = 'B'
FREE_CHAR = '.'
OCCUPIED_CHAR = '-'

INFINITY = 9999999
VERSION = '0.3'

# constants for evaluation function
TURN = 2      # color to move gets + turn
BRV = 3       # multiplier for back rank
KCV = 5       # multiplier for kings in center
MCV = 1       # multiplier for men in center

MEV = 1       # multiplier for men on edge
KEV = 5       # multiplier for kings on edge
CRAMP = 5     # multiplier for cramp

OPENING = 2   # multipliers for tempo
MIDGAME = -1
ENDGAME = 2
INTACTDOUBLECORNER = 3

#   (white)
#      8    37  38  39  40
#      7  32  33  34  35
#      6    28  29  30  31
#      5  23  24  25  26
#      4    19  20  21  22
#      3  14  15  16  17
#      2    10  11  12  13
#      1  5   6   7   8
#         a b c d e f g h
#   (black)

# translate from simple input notation to real checkerboard notation
IMAP = {'a1': 5,  'c1': 6,  'e1': 7,  'g1': 8,
        'b2': 10, 'd2': 11, 'f2': 12, 'h2': 13,
        'a3': 14, 'c3': 15, 'e3': 16, 'g3': 17,
        'b4': 19, 'd4': 20, 'f4': 21, 'h4': 22,
        'a5': 23, 'c5': 24, 'e5': 25, 'g5': 26,
        'b6': 28, 'd6': 29, 'f6': 30, 'h6': 31,
        'a7': 32, 'c7': 33, 'e7': 34, 'g7': 35,
        'b8': 37, 'd8': 38, 'f8': 39, 'h8': 40}

CBMAP = {5:4, 6:3, 7:2, 8:1,
         10:8, 11:7, 12:6, 13:5,
         14:12, 15:11, 16:10, 17:9,
         19:16, 20:15, 21:14, 22:13,
         23:20, 24:19, 25:18, 26:17,
         28:24, 29:23, 30:22, 31:21,
         32:28, 33:27, 34:26, 35:25,
         37:32, 38:31, 39:30, 40:29}

def create_grid_map():
    """ Maps internal board indices to grid (row, col) coordinates """
    grd = {}
    grd[5]  = (7,0); grd[6]  = (7,2); grd[7]  = (7,4); grd[8]  = (7,6)
    grd[10] = (6,1); grd[11] = (6,3); grd[12] = (6,5); grd[13] = (6,7)
    grd[14] = (5,0); grd[15] = (5,2); grd[16] = (5,4); grd[17] = (5,6)
    grd[19] = (4,1); grd[20] = (4,3); grd[21] = (4,5); grd[22] = (4,7)
    grd[23] = (3,0); grd[24] = (3,2); grd[25] = (3,4); grd[26] = (3,6)
    grd[28] = (2,1); grd[29] = (2,3); grd[30] = (2,5); grd[31] = (2,7)
    grd[32] = (1,0); grd[33] = (1,2); grd[34] = (1,4); grd[35] = (1,6)
    grd[37] = (0,1); grd[38] = (0,3); grd[39] = (0,5); grd[40] = (0,7)
    return grd
